import sys
import socket
import os
import base64
import time
import math
import itertools
from collections import defaultdict
import numpy as np

import peer
import eachare
import messageParser
import file as f
import downloadStats

'''
This function is made to handle all the commands a peer receives.
Each peer must initiate this function and it stores the socket that the peer uses to
communicate, the neighbours and the active neighbours
'''
class commandHandler():

    connectionSocket: socket
    inputCommandOptions = ("Escolha um comando:\n" +
                              "\t[1] Listar peers\n" +
                              "\t[2] Obter peers\n" +
                              "\t[3] Listar arquivos locais\n" +
                              "\t[4] Buscar arquivos\n" +
                              "\t[5] Exibir estatisticas\n" +
                              "\t[6] Alterar tamanho de chunk\n" +
                              "\t[9] Sair")
    filesReceived: {}
    activeDownloads: {}
    numberOfAnswers: int
    numberOfAwaitedAnswers: int

    def __init__(self):
        self.filesReceived = {}
        self.activeDownloads = {}
        self.numberOfAnswers = 0
        self.numberOfAwaitedAnswers = 0

    def setConnectionSocket(self, connectionSocket):
        self.connectionSocket = connectionSocket

    def getConnectionSocket(self):
        return self.connectionSocket

    # Imprime o menu de opcoes padrao
    def printCommandOptions(self):
        print(self.inputCommandOptions)

    # Imprime a lista de vizinhos conhecidos
    def printNeighboursList(self, currentPeer):
        i = 0
        print("Lista de peers:\n" +
              f"\t[{i}] voltar para o menu anterior")
        for neighbour in currentPeer.neighbourPeers:
            i+=1
            print(f"\t[{i}] {neighbour}")

    # Updated function for EP3:
    # Checks if the file is repeated on the list in order to print the "peer" column, avoiding replicated entries
    def printFilesList(self):
        print("Arquivos encontrados na rede:")
        print("Nome\t\t| Tamanho\t| Peer(s)")
        print("[0] <Cancelar>")

        # Agrupa arquivos por (nome, tamanho) para identificar arquivos identicos.
        groupedFiles = defaultdict(lambda: {'size': 0, 'peers': []})
        for peerAddr, fileList in self.filesReceived.items():
            for fileInfo in fileList:
                key = (fileInfo['name'], fileInfo['size'])
                groupedFiles[key]['size'] = fileInfo['size']
                # Adiciona o peer na lista de peers que possuem este arquivo.
                if fileInfo['peer'] not in groupedFiles[key]['peers']:
                    groupedFiles[key]['peers'].append(fileInfo['peer'])

        # Cria uma lista formatada para exibicao.
        displayList = [{'name': k[0], 'size': v['size'], 'peers': v['peers']} for k, v in groupedFiles.items()]

        for i, fileInfo in enumerate(displayList, 1):
            peersStr = ", ".join([f"{p[0]}:{p[1]}" for p in fileInfo['peers']])
            print(f"[{i}] {fileInfo['name']}\t| {fileInfo['size']}\t\t| {peersStr}")
        return displayList

    # Encodes
    # Full file
    def encodeFileToBase64(self, filepath):
        with open(filepath, "rb") as file:
            fileContent = file.read()
            encodedContent = base64.b64encode(fileContent)
            return encodedContent.decode('utf-8')

    # Specific chunk
    def encodeFileChunk(self, filepath, offset, chunkSize):
        try:
            with open(filepath, "rb") as file:
                file.seek(offset)
                chunk = file.read(chunkSize)
                encodedContent = base64.b64encode(chunk)
                return encodedContent.decode('utf-8')
        except FileNotFoundError:
            return None

    # Decodes
    # Full file
    def decodeBase64ToFile(self, encoded, outputFilepath):
        decodedFile = base64.b64decode(encoded)
        with open(outputFilepath, "wb") as file:
            file.write(decodedFile)

    # From chunks
    def saveFileFromChunks(self, chunks, outputFilepath):
        with open(outputFilepath, "wb") as file:
            for i in sorted(chunks.keys()):
                decodedChunk = base64.b64decode(chunks[i])
                file.write(decodedChunk)

    # Lida com os comandos recebidos do usuario
    def handleCommand(self, commandedPeer: eachare, command: int):
        match command:
            case 1: # COMANDO HELLO
                self.printNeighboursList(self, commandedPeer.currentPeer)
                chosenPeer = int(input("> "))
                if(chosenPeer == 0):
                    return
                neighbour = commandedPeer.currentPeer.neighbourPeers[chosenPeer-1]
                commandedPeer.currentPeer.increaseClock()
                try:
                    commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(),
                                              commandedPeer.currentPeer.getPort(),
                                              commandedPeer.currentPeer.getClock(),
                                              "HELLO",
                                              neighbour.getAddress(),
                                              neighbour.getPort())
                    print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()}:{neighbour.getClock()} status ONLINE")
                    neighbour.setStatusOnline()
                except ConnectionRefusedError:
                    print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()}:{neighbour.getClock()} status OFFLINE")
                    neighbour.setStatusOffline()
                return

            case 2: # COMANDO GET_PEERS
                for neighbour in commandedPeer.currentPeer.neighbourPeers:
                    try:
                        commandedPeer.currentPeer.increaseClock()
                        commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(),
                                                  commandedPeer.currentPeer.getPort(),
                                                  commandedPeer.currentPeer.getClock(),
                                                  "GET_PEERS",
                                                  neighbour.getAddress(),
                                                  neighbour.getPort())
                        neighbour.setStatusOnline()
                        print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()} status ONLINE")
                        # RECEBER RESPOSTA AQUI!!!
                    except BrokenPipeError:
                        print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()} status OFFLINE")
                        neighbour.setStatusOffline()
                    except ConnectionRefusedError:
                        print(f"Conexao recusada no socket {neighbour}")
                return

            case 3: # COMANDO OBTER_PEERS
                for file in os.listdir(commandedPeer.directory):
                    filename = os.fsdecode(file)
                    print(f"\t{filename}")
                return

            case 4: # COMANDO BUSCAR
                self.numberOfAnswers = 0
                for neighbour in commandedPeer.currentPeer.neighbourPeers:
                    if neighbour.getStatus() == True:
                        try:
                            commandedPeer.currentPeer.increaseClock()
                            commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(),
                                                      commandedPeer.currentPeer.getPort(),
                                                      commandedPeer.currentPeer.getClock(),
                                                      "LS",
                                                      neighbour.getAddress(),
                                                      neighbour.getPort())
                            self.numberOfAwaitedAnswers += 1
                            # print(f"[DEBUG] Awaited answers = {self.numberOfAwaitedAnswers}")
                        except BrokenPipeError:
                            print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()} status OFFLINE")
                            neighbour.setStatusOffline()
                        except ConnectionRefusedError:
                            print(f"Conexao recusada no socket {neighbour}")
                commandedPeer.handleCommands = False
                return

            case 5: # COMANDO EXIBIR ESTATISTICAS
                print("Estatísticas de Download:")
                if not commandedPeer.downloadStatistics:
                    print("Nenhuma estatísticas coletada ainda.")
                    return

                # Agrupando
                statsByKey = defaultdict(list)
                for stat in commandedPeer.downloadStatistics:
                    key = (stat.chunkSize, stat.numPeers, stat.fileSize)
                    statsByKey[key].append(stat.downloadTime)

                print("Tam. chunk | N peers | Tam. arquivo | N | Tempo [s] | Desvio Padrão")
                for key, times in statsByKey.items():
                    chunkSize, numPeers, fileSize = key
                    n = len(times)
                    tempoMedio = np.mean(times)
                    desvioPadrao = np.std(times) if n > 1 else 0
                    print(f"{chunkSize:<10} | {numPeers:<7} | {fileSize:<12} | {n:<1} | {tempoMedio:<9.5f} | {desvioPadrao:<.5f}")
                return

            case 6: # COMANDO ALTERAR TAMANHO DE CHUNK
                try:
                    print("Digite novo tamanho de chunk:")
                    newSize = int(input("> "))
                    if newSize > 0:
                        commandedPeer.setChunkSize(newSize)
                    else:
                        print(f"Tamanho de chunk deve ser um número positivo. O tamanho atual {commandedPeer.getChunkSize()} foi mantido.")
                except ValueError:
                    print("Entrada inválida, por favor digite um número inteiro")
                return

            case 9: # COMANDO SAIR
                # parar de esperar conexões (fechar o socket de conexões)
                commandedPeer.closeListening()
                print("\nSaindo...")
                # enviar mensagem tipo "BYE" para cada peer que estiver online
                for neighbour in commandedPeer.currentPeer.neighbourPeers:
                    if neighbour.getStatus() == True:
                        commandedPeer.currentPeer.increaseClock()
                        # print("[DEBUG] ENVIANDO BYE")
                        commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(),
                                                  commandedPeer.currentPeer.getPort(),
                                                  commandedPeer.currentPeer.getClock(),
                                                  "BYE",
                                                  neighbour.getAddress(),
                                                  neighbour.getPort())
                # terminar execução do programa
                commandedPeer.closeListening()
                commandedPeer.stopReceiving()
                os._exit(0)
            case _:
                print("Esse comando não é reconhecido ou não está implementado")
                return

    # Lida com os comandos recebidos de outros peers
    def handleRemoteCommand(self, receiverPeer, message: str, receiverSocket: socket.socket, senderSocket: socket.socket):

        parser = messageParser.messageParser()
        parser.parse(message)
        senderIP = parser.senderIP
        senderPort = parser.senderPort
        senderClock = parser.senderClock
        messageType = parser.messageType

        # print(f"Mensagem recebida: \"{message}\"")

        if(senderClock > receiverPeer.currentPeer.getClock()):
            receiverPeer.currentPeer.updateClock(senderClock)
        else:
            receiverPeer.currentPeer.increaseClock()

        if "HELLO" == messageType:
            # print("[DEBUG] Recebida mensagem HELLO")
            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer == None):
                newPeer = peer.peer(senderIP, senderPort)
                newPeer.setStatusOnline()
                newPeer.updatePeerClock(0)
                receiverPeer.currentPeer.addNeighbour(newPeer)
                print(f"Adicionado novo peer {newPeer.getAddress()}:{newPeer.getPort()}:{newPeer.getClock()} status {"ONLINE" if newPeer.getStatus() else "OFFLINE"}")
                if(newPeer.getClock() < senderClock):
                    newPeer.updatePeerClock(senderClock)
                print(f"Atualizando peer {newPeer.getAddress()}:{newPeer.getPort()}:{newPeer.getClock()} status {"ONLINE" if newPeer.getStatus() else "OFFLINE"}")
            else:
                findPeer.setStatusOnline()
                if(findPeer.getClock() < senderClock):
                    findPeer.updatePeerClock(senderClock)
                print(f"Atualizando peer {findPeer.getAddress()}:{findPeer.getPort()}:{findPeer.getClock()} status {"ONLINE" if findPeer.getStatus() else "OFFLINE"}")
            print("> ")
        if "GET_PEERS" == messageType:
            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer != None):
                if (findPeer.getClock() < senderClock):
                    findPeer.updatePeerClock(senderClock)
                if(findPeer.getStatus() == False):
                    findPeer.setStatusOnline()
                    print(f"Atualizando peer {findPeer.getAddress()}:{findPeer.getPort()}:{findPeer.getClock()} status {"ONLINE" if findPeer.getStatus() else "OFFLINE"}")
            else:
                receiverPeer.currentPeer.addNeighbour(findPeer)

            responseArgs = f"{len(receiverPeer.currentPeer.neighbourPeers)} "
            for neighbour in receiverPeer.currentPeer.neighbourPeers:
                if not(neighbour.getAddress() == senderIP and neighbour.getPort() == senderPort):
                    responseArgs += f"{neighbour.getAddress()}:{neighbour.getPort()}:{"ONLINE" if neighbour.getStatus() else "OFFLINE"}:{neighbour.getClock()} "
            receiverPeer.currentPeer.increaseClock()
            receiverPeer.sendMessage(receiverPeer.currentPeer.getAddress(),
                                     receiverPeer.currentPeer.getPort(),
                                     receiverPeer.currentPeer.getClock(),
                                     "PEER_LIST " + responseArgs,
                                     senderIP,
                                     senderPort)
            print("> ")
        if "PEER_LIST" == messageType:

            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer != None):
                if (findPeer.getClock() < senderClock):
                    findPeer.updatePeerClock(senderClock)
                if(findPeer.getStatus() == False):
                    findPeer.setStatusOnline()
                    print(f"Atualizando peer {findPeer.getAddress()}:{findPeer.getPort()}:{findPeer.getClock()} status {"ONLINE" if findPeer.getStatus() else "OFFLINE"}")
            else:
                receiverPeer.currentPeer.addNeighbour(receiverPeer.currentPeer, findPeer)

            # The next part is the number of peers in the list
            numPeers = message.split(" ")[1]

            # The next part is the type of message (PEER_LIST), we don't need to do anything with it here
            messageType = message.split(" ")[2]

            # The number of peers (num_peers) should be followed by the actual peer list
            sentPeers = " ".join(message.split(" ")[4:])  # Get the remaining part that contains peer information
            peers = sentPeers.strip().split(" ")  # Split into individual peer entries

            for sentPeer in peers:
                # separa informacao do peer
                peerInfo = sentPeer.split(":")
                peerIP = peerInfo[0]
                peerPort = int(peerInfo[1])
                peerStatus = peerInfo[2]
                peerClock = int(peerInfo[3])

                # Find the peer in the list based on IP and port
                findPeer = self.findPeerInList(self, receiverPeer.currentPeer, peerIP, peerPort)

                # If the peer is not found in the current list, add it
                if findPeer is None:
                    # Create a new peer object and add it to the neighbour list
                    newPeer = peer.peer(peerIP, peerPort)
                    receiverPeer.currentPeer.addNeighbour(newPeer)

                    # Set the peer's status based on the message
                    if peerStatus == "ONLINE":
                        newPeer.setStatusOnline()
                    elif peerStatus == "OFFLINE":
                        newPeer.setStatusOffline()

                    newPeer.updatePeerClock(peerClock)
                    receiverPeer.currentPeer.addNeighbour(newPeer)
                    print(f"Adicionado novo peer {newPeer.getAddress()}:{newPeer.getPort()}:{newPeer.getClock()} status {"ONLINE" if newPeer.getStatus() else "OFFLINE"}")

                elif findPeer.getClock() < peerClock:
                    # If the peer is already in the list and the new clock is higher, update its status and clock
                    if peerStatus == "ONLINE":
                        findPeer.setStatusOnline()
                    elif peerStatus == "OFFLINE":
                        findPeer.setStatusOffline()

                    findPeer.updatePeerClock(peerClock)

                    print(f"Atualizando peer {findPeer.getAddress()}:{findPeer.getPort()}:{findPeer.getClock()} status {"ONLINE" if findPeer.getStatus() else "OFFLINE"}")
            print("> ")
        if "LS" == messageType:

            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer != None):
                if (findPeer.getClock() < senderClock):
                    findPeer.updatePeerClock(senderClock)
                if(findPeer.getStatus() == False):
                    findPeer.setStatusOnline()
                    print(f"Atualizando peer {findPeer.getAddress()}:{findPeer.getPort()}:{findPeer.getClock()} status {"ONLINE" if findPeer.getStatus() else "OFFLINE"}")
            else:
                receiverPeer.currentPeer.addNeighbour(findPeer)

            numberOfFiles = 0
            for file in os.listdir(receiverPeer.directory):
                numberOfFiles += 1
            responseArgs = f"{numberOfFiles}"

            for file in os.listdir(receiverPeer.directory):
                filename = os.fsdecode(file)
                path = f"{receiverPeer.directory}/{filename}"
                responseArgs += f" {filename}:{os.stat(path).st_size}"
            receiverPeer.currentPeer.increaseClock()
            receiverPeer.sendMessage(receiverPeer.currentPeer.getAddress(),
                                     receiverPeer.currentPeer.getPort(),
                                     receiverPeer.currentPeer.getClock(),
                                     "LS_LIST " + responseArgs,
                                     senderIP,
                                     senderPort)
            print("> ")
            return
        if "LS_LIST" == messageType:

            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer != None):
                if (findPeer.getClock() < senderClock):
                    findPeer.updatePeerClock(senderClock)
                if(findPeer.getStatus() == False):
                    findPeer.setStatusOnline()
                    print(f"Atualizando peer {findPeer.getAddress()}:{findPeer.getPort()}:{findPeer.getClock()} status {"ONLINE" if findPeer.getStatus() else "OFFLINE"}")
            else:
                findPeer.setStatusOnline()
                receiverPeer.currentPeer.addNeighbour(receiverPeer.currentPeer, findPeer)

            self.numberOfAnswers += 1

            # Processa a string de arquivos recebida.
            parts = message.split(" ")
            filesStr = parts[4:]

            # Armazena os arquivos recebidos associados ao peer que respondeu.
            # Esta estrutura de dicionário é usada para depois agrupar arquivos idênticos.
            peerKey = f"{senderIP}:{senderPort}"
            self.filesReceived[peerKey] = []
            for fileInfoStr in filesStr:
                if ':' not in fileInfoStr: continue  # Pula entradas malformadas
                try:
                    name, sizeStr = fileInfoStr.split(':')
                    size = int(sizeStr)
                    # Adiciona a informação do arquivo e do peer de origem.
                    self.filesReceived[peerKey].append({
                        'name': name,
                        'size': size,
                        'peer': (senderIP, senderPort)
                    })
                except ValueError:
                    # Ignora arquivos com formato de tamanho inválido.
                    continue

            # A lógica a seguir só é executada quando todas as respostas LS_LIST foram recebidas.
            if self.numberOfAnswers >= self.numberOfAwaitedAnswers:
                # Usa a função para imprimir a lista de arquivos agrupada.
                displayList = self.printFilesList(self)
                try:
                    choice = int(input("Digite o numero do arquivo para fazer o download:\n> "))
                    if choice == 0:
                        # Limpa os dados para a próxima busca.
                        self.filesReceived.clear()
                        self.numberOfAnswers = 0
                        self.numberOfAwaitedAnswers = 0
                        receiverPeer.handleCommands = True
                        return

                    # Obtém as informações do arquivo escolhido a partir da lista exibida.
                    selectedFile = displayList[choice - 1]
                    filename = selectedFile['name']
                    filesize = selectedFile['size']
                    peersWithFile = selectedFile['peers']

                    # Inicia a lógica de download em chunks.
                    chunkSize = receiverPeer.getChunkSize()
                    numChunks = math.ceil(filesize / chunkSize)
                    downloadKey = f"{filename}:{filesize}"

                    self.activeDownloads[downloadKey] = {
                        'chunks': {},
                        'expectedChunks': numChunks,
                        'peers': peersWithFile,
                        'startTime': time.time()
                    }

                    # Usa o Round-Robin (itertools.cycle) do seu código original para distribuir
                    # o pedido dos chunks entre os peers que possuem o arquivo.
                    peerCycle = itertools.cycle(peersWithFile)
                    for i in range(numChunks):
                        # Pega o próximo peer da lista circular.
                        peerIp, peerPort = next(peerCycle)

                        receiverPeer.currentPeer.increaseClock()
                        # Monta a mensagem DL com o índice do chunk (i).
                        dlMessage = f"DL {filename} {i} {chunkSize}"
                        receiverPeer.sendMessage(receiverPeer.currentPeer.getAddress(),
                                                 receiverPeer.currentPeer.getPort(),
                                                 receiverPeer.currentPeer.getClock(),
                                                 dlMessage,
                                                 peerIp,
                                                 peerPort)
                except (ValueError, IndexError):
                    print("Seleção inválida.")
                    receiverPeer.handleCommands = True
                finally:
                    # Limpa os dados para a próxima busca, independentemente do que acontecer.
                    self.filesReceived.clear()
                    self.numberOfAnswers = 0
                    self.numberOfAwaitedAnswers = 0
            return

        if "DL" == messageType:
            filename = message.split(" ")[3]
            chunkIndex = int(message.split(" ")[4])
            chunkSize = int(message.split(" ")[5])

            filepath = os.path.join(receiverPeer.directory, filename)
            offset = chunkIndex * chunkSize

            # Le e codifica o chunk solicitado
            encodedChunk = self.encodeFileChunk(self, filepath, offset, chunkSize)

            if encodedChunk:
                receiverPeer.currentPeer.increaseClock()
                fileMessage = f"FILE {filename} {chunkIndex} {encodedChunk}"
                receiverPeer.sendMessage(receiverPeer.currentPeer.getAddress(),
                                         receiverPeer.currentPeer.getPort(),
                                         receiverPeer.currentPeer.getClock(),
                                         fileMessage,
                                         senderIP,
                                         senderPort)
            return

        if "FILE" == messageType:
            filename = message.split(" ")[3]
            chunkIndex = int(message.split(" ")[4])
            encodedChunk = message.split(" ")[5]

            # Encontra o download correspondente na lista de downloads ativos.
            downloadKey = next((key for key in self.activeDownloads if key.startswith(f"{filename}:")), None)

            if downloadKey:
                downloadInfo = self.activeDownloads[downloadKey]
                downloadInfo['chunks'][chunkIndex] = encodedChunk

                # Se todos os chunks foram recebidos, finaliza o download.
                if len(downloadInfo['chunks']) == downloadInfo['expectedChunks']:
                    endTime = time.time()  # Finaliza a contagem de tempo.

                    outputPath = os.path.join(receiverPeer.directory, filename)
                    # Salva o arquivo a partir dos chunks.
                    self.saveFileFromChunks(self, downloadInfo['chunks'], outputPath)
                    print(f"Download do arquivo {filename} finalizado.")

                    # Coleta e armazena as estatisticas do download.
                    filesize = int(downloadKey.split(':')[1])
                    elapsedTime = endTime - downloadInfo['startTime']
                    stat = downloadStats.DownloadStats(
                        chunkSize=receiverPeer.getChunkSize(),
                        numPeers=len(downloadInfo['peers']),
                        fileSize=filesize,
                        downloadTime=elapsedTime
                    )
                    receiverPeer.downloadStatistics.append(stat)

                    # Limpa o registro do download.
                    del self.activeDownloads[downloadKey]
                    receiverPeer.handleCommands = True
            return

        if "BYE" == messageType:
            # print("[DEBUG] Recebida mensagem BYE")
            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer == None):
                newPeer = peer.peer(senderIP, senderPort)
                newPeer.setStatusOffline()
                receiverPeer.currentPeer.addNeighbour(receiverPeer.currentPeer, newPeer)
            else:
                findPeer.setStatusOffline()

            print("> ")

    def findPeerInList(self, currentPeer, IP:str, port:int):
        for p in currentPeer.neighbourPeers:
            if IP == p.getAddress() and port == p.getPort():
                return p
        return None
