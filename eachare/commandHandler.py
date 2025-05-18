import sys
import socket
import os

import peer
import eachare
import messageParser

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

    def __init__(self):
        pass

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

    def handleCommand(self, commandedPeer: eachare, command: int):
        match command:
            case 1: # COMANDO HELLO
                self.printNeighboursList(self, commandedPeer.currentPeer)
                chosenPeer = int(input("> "))
                if(chosenPeer == 0):
                    return
                neighbour = commandedPeer.currentPeer.neighbourPeers[chosenPeer-1]
                commandedPeer.increaseLocalClock()
                try:
                    commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(),
                                              commandedPeer.currentPeer.getPort(),
                                              commandedPeer.getLocalClock(),
                                              "HELLO",
                                              neighbour.getAddress(),
                                              neighbour.getPort())
                    print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()} status ONLINE")
                    neighbour.setStatusOnline()
                except ConnectionRefusedError:
                    print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()} status OFFLINE")
                    neighbour.setStatusOffline()
                return
            case 2: # COMANDO GET_PEERS
                for neighbour in commandedPeer.currentPeer.neighbourPeers:
                    try:
                        commandedPeer.increaseLocalClock()
                        commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(),
                                                  commandedPeer.currentPeer.getPort(),
                                                  commandedPeer.getLocalClock(),
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
            case 3: # COMANDO OBTER_PEERS !!DEBUG ARRUMAR vou me matar
                for file in os.listdir(commandedPeer.directory):
                    filename = os.fsdecode(file)
                    print(f"\t{filename}")
                return
            case 9:
                # parar de esperar conexões (fechar o socket de conexões)
                commandedPeer.closeListening()
                print("\nSaindo...")
                # aumentar clock local
                commandedPeer.increaseLocalClock()
                # enviar mensagem tipo "BYE" para cada peer que estiver online
                for neighbour in commandedPeer.currentPeer.neighbourPeers:
                    if neighbour.getStatus == "ONLINE":
                        print("!!DEBUG ENVIANDO BYE")
                        commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(commandedPeer.currentPeer),
                                                  commandedPeer.currentPeer.getPort(commandedPeer.currentPeer),
                                                  commandedPeer.getLocalClock(),
                                                  "BYE",
                                                  neighbour.getAddress(),
                                                  neighbour.getPort())
                # terminar execução do programa
                sys.exit(f"Programa encerrado por comando do usuário")
            case _:
                print("Esse comando não é reconhecido ou não está implementado")
                return

    def handleRemoteCommand(self, receiverPeer, message: str, receiverSocket: socket.socket, senderSocket: socket.socket):

        parser = messageParser.messageParser()
        parser.parse(message)
        senderIP = parser.senderIP
        senderPort = parser.senderPort
        senderClock = parser.senderClock # esse clock no momento é local, mas imagino que futuramente virará global
        messageType = parser.messageType

        print(f"Mensagem recebida: \"{message}\"")

        if "HELLO" in messageType:
            # print("[DEBUG] Recebida mensagem HELLO")
            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer == None):
                newPeer = peer.peer(senderIP, senderPort)
                newPeer.setStatusOnline()
                receiverPeer.currentPeer.addNeighbour(receiverPeer.currentPeer, newPeer)
                f = open(receiverPeer.neighboursFile, "a")
                f.write(f"{senderIP}:{senderPort}\n")
            else:
                findPeer.setStatusOnline()
        if "GET_PEERS" in messageType:
            responseArgs = f"{len(receiverPeer.currentPeer.neighbourPeers)} "
            for neighbour in receiverPeer.currentPeer.neighbourPeers:
                responseArgs += f"{neighbour.getAddress()}:{neighbour.getPort()}:{"ONLINE" if neighbour.getStatus() else "OFFLINE"}:0 "
            receiverPeer.increaseLocalClock()
            receiverPeer.sendMessage(receiverPeer.currentPeer.getAddress(),
                                     receiverPeer.currentPeer.getPort(),
                                     receiverPeer.getLocalClock(),
                                     "PEER_LIST " + responseArgs,
                                     senderIP,
                                     senderPort)
        if "PEER_LIST" in messageType:
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
                peerPort = peerInfo[1]
                peerStatus = peerInfo[2]

                # Find the peer in the list based on IP and port
                findPeer = self.findPeerInList(self, receiverPeer.currentPeer, peerIP, peerPort)

                # If the peer is not found in the current list, add it
                if findPeer is None and not(peerIP == receiverPeer.currentPeer.getAddress() and peerPort == receiverPeer.currentPeer.getPort()):
                    # Create a new peer object and add it to the neighbour list
                    newPeer = peer.peer(peerIP, peerPort)
                    receiverPeer.currentPeer.addNeighbour(newPeer)

                    # Set the peer's status based on the message
                    if peerStatus == "ONLINE":
                        newPeer.setStatusOnline()
                    elif peerStatus == "OFFLINE":
                        newPeer.setStatusOffline()

                else:
                    # If the peer is already in the list, just update its status
                    if peerStatus == "ONLINE":
                        findPeer.setStatusOnline()
                    elif peerStatus == "OFFLINE":
                        findPeer.setStatusOffline()
        if "BYE" in messageType:
            # print("[DEBUG] Recebida mensagem BYE")
            findPeer = self.findPeerInList(self, receiverPeer.currentPeer, senderIP, senderPort)
            if(findPeer == None):
                newPeer = peer.peer(senderIP, senderPort)
                newPeer.setStatusOffline()
                receiverPeer.currentPeer.addNeighbour(receiverPeer.currentPeer, newPeer)
                f = open(receiverPeer.neighboursFile, "a")
                f.write(f"{senderIP}:{senderPort}\n")
            else:
                findPeer.setStatusOffline()


    def findPeerInList(self, currentPeer, IP:str, port:int):
        for p in currentPeer.neighbourPeers:
            pIP = p.getAddress()
            pPort = p.getPort()
            print(f"!!DEBUG COMPARING {p} TO {IP}:{port}")
            if IP == pIP and port == pPort:
                print("!!DEBUG MATCH")
                return p
            print("!!DEBUG NO MATCH")
        return None