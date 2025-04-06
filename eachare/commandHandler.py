import sys
import socket
import this

import peer
import eachare

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
            case 1:
                self.printNeighboursList(self, commandedPeer.currentPeer)
                chosenPeer = int(input("> "))
                if(chosenPeer == 0):
                    return
                neighbour = commandedPeer.currentPeer.neighbourPeers[chosenPeer]
                commandedPeer.increaseLocalClock()
                try:
                    commandedPeer.sendMessage(commandedPeer.currentPeer.getAddress(commandedPeer.currentPeer),
                                              commandedPeer.currentPeer.getPort(commandedPeer.currentPeer),
                                              commandedPeer.getLocalClock(),
                                              "HELLO",
                                              neighbour.getAddress(),
                                              neighbour.getPort())
                    print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()} status ONLINE")
                    neighbour.setStatusOnline()

                except BrokenPipeError:
                    print(f"Atualizando peer {neighbour.getAddress()}:{neighbour.getPort()} status OFFLINE")
                    neighbour.setStatusOffline()
                return
            case 9:
                # parar de esperar conexões (fechar o socket de conexões)
                commandedPeer.closeListening()
                print("\nSaindo...")
                # aumentar clock local
                commandedPeer.increaseLocalClock()
                # enviar mensagem tipo "BYE" para cada peer que estiver online
                for neighbour in commandedPeer.currentPeer.neighbourPeers:
                    if neighbour.getStatus == True:
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

    def handleRemoteCommand(self, message: str, receiverSocket: socket.socket):
        # gramatica da mensagem:
        # <ORIGEM> <CLOCK> <TIPO>[ ARGUMENTO1 ARGUMENTO2...]\n
        senderIP = message.split(" ")[0].split(":")[0]
        senderPort = int(message.split(" ")[0].split(":")[1])
        senderClock = int(message.split(" ")[1]) # esse clock no momento é local, mas imagino que futuramente virará global
        messageType = message.split(" ")[2]
        messageArgs : List[str] = message.split("[ ")[1:]

        if "HELLO" in command:
            peer = findPeerInList(senderIP, senderPort)
            if(peer == None):
                peer = peer.Peer(senderIP, senderPort)
                peer.setStatusOnline()
                self.addNeighbour(peer)

    def findPeerInList(self, IP:str, port:int):
        for p in neighbourList:
            if(IP == p.getAddress() and port == p.getPort()):
                return p

        return None