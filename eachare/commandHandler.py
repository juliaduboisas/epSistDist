import sys
import socket
import os
import base64

import peer
import eachare
import messageParser
import file as f

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
    filesReceived: []
    numberOfAnswers: int
    numberOfAwaitedAnswers: int

    def __init__(self):
        self.filesReceived = []
        self.numberOfAnswers = 0
        self.numberOfAwaitedAnswers = 0

    def setConnectionSocket(self, connectionSocket):
        self.connectionSocket = connectionSocket

    def getConnectionSocket(self):
        return self.connectionSocket

    def printCommandOptions(self):
        print(self.inputCommandOptions)

    def printNeighboursList(self, currentPeer):
        i = 0
        print("Lista de peers:\n" +
              f"\t[{i}] voltar para o menu anterior")
        for neighbour in currentPeer.neighbourPeers:
            i+=1
            print(f"\t[{i}] {neighbour}")

    def printFilesList(self):
        i = 0
        print("Arquivos encontrados na rede: \n" +
              f"\t[{i}] Cancelar")
        for file in self.filesReceived:
            i+=1
            print(f"\t[{i}] {file}")

    def encodeFileToBase64(self, filepath):
        with open(filepath, "rb") as file:
            file_content = file.read()
            encoded_content = base64.b64encode(file_content)
            return encoded_content.decode('utf-8')

    def decodeBase64ToFile(self, encoded, outputFilepath):
        decodedFile = base64.b64decode(encoded)
        with open(outputFilepath, "wb") as file:
            file.write(decodedFile)

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
                for neighbour in commandedPeer.currentPeer.neighbourPeers:
                    if neighbour.getStatus() == True:
                        commandedPeer.currentPeer.increaseClock()
                        commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(),
                                                  commandedPeer.currentPeer.getPort(),
                                                  commandedPeer.currentPeer.getClock(),
                                                  "LS",
                                                  neighbour.getAddress(),
                                                  neighbour.getPort())
                        self.numberOfAwaitedAnswers += 1
                        # print(f"[DEBUG] Awaited answers = {self.numberOfAwaitedAnswers}")
                commandedPeer.handleCommands = False
                return
            case 9:
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

    def handleRemoteCommand(self, receiverPeer, message: str, receiverSocket: socket.socket, senderSocket: socket.socket):

        parser = messageParser.messageParser()
        parser.parse(message)
        senderIP = parser.senderIP
        senderPort = parser.senderPort
        senderClock = parser.senderClock
        messageType = parser.messageType

        print(f"Mensagem recebida: \"{message}\"")

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
                receiverPeer.currentPeer.addNeighbour(receiverPeer.currentPeer, newPeer)
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
            if(findPeer != None) and (findPeer.getClock() < senderClock):
                findPeer.setStatusOnline()
                findPeer.updatePeerClock(senderClock)
                print(f"Atualizando peer {findPeer.getAddress()}:{findPeer.getPort()}:{findPeer.getClock()} status {"ONLINE" if findPeer.getStatus() else "OFFLINE"}")

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
            # The next part is the number of peers in the list
            num_peers = message.split(" ")[1]

            # The next part is the type of message (PEER_LIST), we don't need to do anything with it here
            message_type = message.split(" ")[2]

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
            numFiles = message.split(" ")[3]
            sentFiles = " ".join(message.split(" ")[4:])  # Get the remaining part that contains peer information
            files = sentFiles.strip().split(" ")

            for file in files:
                name = file.split(":")[0]
                size = int(file.split(":")[1])
                receivedFile = f.file(name, size, senderIP, senderPort)
                self.filesReceived.append(receivedFile)

            self.numberOfAnswers += 1
            # print(f"[DEBUG] Number of received answers = {self.numberOfAnswers}")

            if self.numberOfAnswers == self.numberOfAwaitedAnswers:
                self.printFilesList(self)
                print("Digite o numero do arquivo para fazer o download:")
                chosenFile = int(input("> "))
                if(chosenFile == 0):
                    self.filesReceived.clear()
                    self.numberOfAnswers = 0
                    self.numberOfAwaitedAnswers = 0
                    # print(f"[DEBUG] Number of received answers = {self.numberOfAnswers}")
                    # print(f"[DEBUG] Awaited answers = {self.numberOfAwaitedAnswers}")
                    receiverPeer.handleCommands = True
                    return
                downloadFile = self.filesReceived[chosenFile-1]
                receiverPeer.currentPeer.increaseClock()
                receiverPeer.sendMessage(receiverPeer.currentPeer.getAddress(),
                                          receiverPeer.currentPeer.getPort(),
                                          receiverPeer.currentPeer.getClock(),
                                          f"DL {downloadFile.getFilename()} 0 0",
                                          downloadFile.getPeerIP(),
                                          downloadFile.getPeerPort())
            return
        if "DL" == messageType:
            filename = message.split(" ")[3]
            filepath = f"{receiverPeer.directory}/{filename}"
            encodedFile = self.encodeFileToBase64(self, filepath)
            receiverPeer.sendMessage(receiverPeer.currentPeer.getAddress(),
                                     receiverPeer.currentPeer.getPort(),
                                     receiverPeer.currentPeer.getClock(),
                                     f"FILE {filename} 0 0 {encodedFile}",
                                     senderIP,
                                     senderPort)
            return
        if "FILE" == messageType:

            filename = message.split(" ")[3]
            encodedFile = message.split(" ")[6]
            decodedFile = self.decodeBase64ToFile(self, encodedFile, f"{receiverPeer.directory}/{filename}")
            self.filesReceived.clear()
            self.numberOfAnswers = 0
            self.numberOfAwaitedAnswers = 0
            print(f"Download do arquivo {filename} finalizado.")
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
            pIP = p.getAddress()
            pPort = p.getPort()
            # print(f"[DEBUG] Comparando {p} com {IP}:{port}")
            if IP == pIP and port == pPort:
                # print("[DEBUG] Match")
                return p
            # print("[DEBUG] Sem match")
        return None