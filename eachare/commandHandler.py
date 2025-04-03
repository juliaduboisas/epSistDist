import sys

import peer

'''
This function is made to handle all the commands a peer receives.
Each peer must initiate this function and it stores the socket that the peer uses to
communicate, the neighbours and the active neighbours
'''
class commandHandler():

    connectionSocket: socket
    neighbourList: List[peer]

    def setConnectionSocket(connectionSocket):
        this.connectionSocket = connectionSocket

    def getConnectionSocket():
        return this.connectionSocket

    def setNeighbourList(neighbourList):
        this.neighbourList = neighbourList

    def getNeighbourList():
        return this.neighbourList

    def addNeighbour(neighbour):
        this.neighbourList.append(neighbour)

    def setActiveNeighbourList(activeNeighbourList):
        this.activeNeighbourList = activeNeighbourList

    def getActiveNeighbourList():
        return this.activeNeighbourList

    def addActiveNeighbour(activeNeighbour):
        this.activeNeighbourList.append(activeNeighbour)

    def handleCommand(command):
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

    def handleRemoteCommand(command, localSocket, remoteSocket):
        if "HELLO" in command:

