import sys
import socket
import this

import peer

'''
This function is made to handle all the commands a peer receives.
Each peer must initiate this function and it stores the socket that the peer uses to
communicate, the neighbours and the active neighbours
'''
class commandHandler():

    connectionSocket: socket

    def __init__(self):
        pass

    def setConnectionSocket(self, connectionSocket):
        self.connectionSocket = connectionSocket

    def getConnectionSocket(self):
        return self.connectionSocket

    def handleCommand(self, command):
        match command:
            case 1:
                return "HELLO"
            case 9:
                # enviar mensagem tipo "BYE" para cada peer que estiver online
                # parar de esperar conexões (fechar o socket de conexões)
                # terminar execução do programa
                sys.exit(f"Programa encerrado por comando do usuário")
            case _:
                return "Esse comando não é reconhecido"

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