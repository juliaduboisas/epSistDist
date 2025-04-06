import socket
import sys
import threading

import commandHandler as ch
import inputArgumentsChecker as argChecker
import peer as p

class eachare():

    currentPeer: p
    peerSocket: socket.socket()
    handler: ch
    listening: bool
    localClock: int
    neighboursFile: str
    directory: str

    def receiveConnections(self):
        print(f"[DEBUG] Socket {self.peerSocket} ouvindo.")
        while self.listening:
            self.peerSocket.listen()
            # se pegar uma conexão, passar para uma outra porta de socket? e manter a escolhida
            # aberta para conexões (eu ACHO)
        (f"[DEBUG] Thread de listen fechando.")
        return

    def receiveCommands(self):
        print(f"[DEBUG] Socket {self.peerSocket} existente para mandar comandos.")
        # INICIO DA EXECUCAO DO PROGRAMA
        while True:
            # IMPRIMIR OPCOES
            self.handler.printCommandOptions(self.handler)
            # RECEBER ENTRADA
            command = int(input("> "))
            # PROCESSAR ENTRADA
            self.handler.handleCommand(self.handler, self, command)

    def getLocalClock(self):
        return self.localClock

    def increaseLocalClock(self):
        self.localClock += 1
        print(f"=> Atualizando relogio para {self.localClock}")

    def openListening(self):
        self.listening = True

    def closeListening(self):
        self.listening = False

    def sendMessage(self, senderAddress, senderPort, clock, type, receiverAddress, receiverPort):
        message = f"{senderAddress}:{senderPort} {clock} {type}"
        print(f"Encaminhando mensagem \"{message}\" para {receiverAddress}:{receiverPort}")
        self.peerSocket.send(message.encode())

    def startProgram(self):
        # RECEBENDO O INPUT DA LINHA DE COMANDO
        inputCheck = argChecker.inputArgumentsChecker(sys.argv)
        inputCheck.checkAll()
        address = sys.argv[1].split(":")[0]
        port = int(sys.argv[1].split(":")[1])
        self.neighboursFile = sys.argv[2]
        self.directory = sys.argv[3]
        print("[DEBUG] Argumentos separados no programa principal.")

        # COLOCANDO NO SOCKET
        self.peerSocket = socket.socket()
        self.peerSocket.bind((address, port))
        print("[DEBUG] Socket criado.")

        # CRIANDO O PEER ATUAL
        self.currentPeer = p.peer
        self.currentPeer.__init__(self.currentPeer, address, port)

        # INICIANDO RELOGIO LOCAL
        # funcionamento do relogio local
        # - antes de enviar uma mensagem, incrementa o clock em 1
        # - ao receber uma mensagem, incrementa o clock em 1
        # - Sempre que o valor do relógio for atualizado, uma mensagem deverá ser exibida na
        #   saída padrão com o seguinte formato: "=> Atualizando relogio para <valor>"

        # inicia o clock do peer
        self.localClock = 0
        print(f"[DEBUG] Clock iniciado em {self.localClock}.")

        # INSTANCIANDO O COMMAND HANDLER
        self.handler = ch.commandHandler
        # inicia o handler do peer
        self.handler.__init__(self.handler)
        print(f"[DEBUG] Command handler iniciado.")

        # CRIANDO A THREAD DE CONEXÕES
        # essa thread mantém o socket aberto para escutar novas conexões
        # e, quando recebe uma nova conexão, a passa para uma nova porta
        # e inicia uma nova thread de comunicação
        print(f"[DEBUG] Iniciando thread de listen no socket {self.peerSocket}.")
        self.openListening()
        receiveConnectionsThread = threading.Thread(target=self.receiveConnections, args=())
        receiveConnectionsThread.start()
        print("[DEBUG] Thread de listen criada.")

        # SALVANDO OS PEERS DO ARQUIVO DE VIZINHOS
        self.currentPeer.makeNeighbourList(self.currentPeer, self.neighboursFile)


        # CRIANDO A THREAD DE COMANDOS
        # essa thread recebe os comandos do usuário
        print(f"[DEBUG] Iniciando thread de comandos.")
        receiveCommandsThread = threading.Thread(target=self.receiveCommands(), args=())
        receiveCommandsThread.start()
        print("[DEBUG] Thread de comandos criada.")

if __name__ == '__main__':
    eachare = eachare()
    eachare.startProgram()