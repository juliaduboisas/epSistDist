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
    receiving: bool
    neighboursFile: str
    directory: str
    chunkSize: int
    handleCommands: bool

    def receiveConnections(self):
        # print(f"[DEBUG] Socket {self.peerSocket} ouvindo.")
        while self.listening:
            self.peerSocket.listen()
            connectionSocket, address = self.peerSocket.accept()
            # print("[DEBUG] Recebida conexao.")
            # print("[DEBUG] Criando nova thread para a conexao.")
            connectionThread = threading.Thread(target=self.connectionThread, args=(connectionSocket, address))
            connectionThread.start()
            # print("[DEBUG] Nova thread criada para receber a mensagem da conexao.")
            # print("[DEBUG] Ouvindo novamente.")
        # (f"[DEBUG] Thread de listen fechando.")
        self.peerSocket.close()
        return

    def connectionThread(self, connectionSocket, address):
        message = self.recvUntilNewline(connectionSocket)
        self.handler.handleRemoteCommand(self.handler, self, message, connectionSocket, self.peerSocket)
        connectionSocket.close()
        return

    def recvUntilNewline(self, sock: socket.socket):
        buffer = b''
        while True:
            data = sock.recv(1024)
            if not data:
                break  # conexão fechada
            buffer += data
            if b'\n' in buffer:
                break
        line, _, rest = buffer.partition(b'\n')
        return line.decode()

    def receiveCommands(self):
        # print(f"[DEBUG] Socket {self.peerSocket} existente para mandar comandos.")
        # INICIO DA EXECUCAO DO PROGRAMA
        while self.receiving:
            if self.handleCommands == True:
                # IMPRIMIR OPCOES
                self.handler.printCommandOptions(self.handler)
                # RECEBER ENTRADA
                command = int(input("> "))
                # PROCESSAR ENTRADA
                self.handler.handleCommand(self.handler, self, command)
        return


    def openListening(self):
        self.listening = True

    def closeListening(self):
        self.listening = False

    def startReceiving(self):
        self.receiving = True

    def stopReceiving(self):
        self.receiving = False

    def sendMessage(self, senderAddress, senderPort, clock, type, receiverAddress, receiverPort):
        message = f"{senderAddress}:{senderPort} {clock} {type}"
        print(f"Encaminhando mensagem \"{message}\" para {receiverAddress}:{receiverPort}")
        senderSocket = socket.socket()
        senderSocket.connect((receiverAddress, receiverPort))
        senderSocket.send(message.encode())
        senderSocket.close()

    def startProgram(self):
        # RECEBENDO O INPUT DA LINHA DE COMANDO
        inputCheck = argChecker.inputArgumentsChecker(sys.argv)
        inputCheck.checkAll()
        address = sys.argv[1].split(":")[0]
        port = int(sys.argv[1].split(":")[1])
        self.neighboursFile = sys.argv[2]
        self.directory = sys.argv[3]
        # print("[DEBUG] Argumentos separados no programa principal.")

        # DETERMINANDO O TAMANHO INICIAL DO CHUNK
        self.chunkSize = 256 # comandado no documento do ep

        # COLOCANDO NO SOCKET
        self.peerSocket = socket.socket()
        self.peerSocket.bind((address, port))
        # print("[DEBUG] Socket criado.")

        # CRIANDO O PEER ATUAL
        self.currentPeer = p.peer(address, port)

        # INSTANCIANDO O COMMAND HANDLER
        self.handler = ch.commandHandler
        # inicia o handler do peer
        self.handler.__init__(self.handler)
        # print(f"[DEBUG] Command handler iniciado.")

        # CRIANDO A THREAD DE CONEXÕES
        # essa thread mantém o socket aberto para escutar novas conexões
        # e, quando recebe uma nova conexão, a passa para uma nova porta
        # e inicia uma nova thread de comunicação
        # print(f"[DEBUG] Iniciando thread de listen no socket {self.peerSocket}.")
        self.openListening()
        self.startReceiving()
        receiveConnectionsThread = threading.Thread(target=self.receiveConnections, args=())
        receiveConnectionsThread.start()
        # print("[DEBUG] Thread de listen criada.")

        # SALVANDO OS PEERS DO ARQUIVO DE VIZINHOS
        self.currentPeer.makeNeighbourList(self.neighboursFile)


        # CRIANDO A THREAD DE COMANDOS
        # essa thread recebe os comandos do usuário
        # print(f"[DEBUG] Iniciando thread de comandos.")
        self.handleCommands = True
        receiveCommandsThread = threading.Thread(target=self.receiveCommands, args=())
        receiveCommandsThread.start()
        # print("[DEBUG] Thread de comandos criada.")

if __name__ == '__main__':
    eachare = eachare()
    eachare.startProgram()