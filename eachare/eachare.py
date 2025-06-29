import socket
import sys
import threading
import time
import math
import numpy as np

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
    downloadStatistics: []

    def getChunkSize(self):
        return self.chunkSize

    def setChunkSize(self, size):
        self.chunkSize = size
        print(f"\tTamanho de chunk alterado: {self.chunkSize}")

    def receiveConnections(self):
        # print(f"[DEBUG] Socket {self.peerSocket} ouvindo.")
        while self.listening:
            try:
                self.peerSocket.listen()
                connectionSocket, address = self.peerSocket.accept()
                # print("[DEBUG] Recebida conexao.")
                # print("[DEBUG] Criando nova thread para a conexao.")
                connectionThread = threading.Thread(target=self.connectionThread, args=(connectionSocket, address))
                connectionThread.start()
                # print("[DEBUG] Nova thread criada para receber a mensagem da conexao.")
                # print("[DEBUG] Ouvindo novamente.")
            except OSError: # if the main socket is closed
                break
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
                try: # garantia que os comandos vao funcionar
                    self.handler.printCommandOptions(self.handler)
                    # RECEBER ENTRADA
                    command = int(input("> "))
                    # PROCESSAR ENTRADA
                    self.handler.handleCommand(self.handler, self, command)
                except ValueError:
                    print("Por favor, insira um novo comando")
        return

    # Controle do recebimento de conexoes
    def openListening(self):
        self.listening = True

    def closeListening(self):
        self.listening = False

    # Controle do recebimento de comandos
    def startReceiving(self):
        self.receiving = True

    def stopReceiving(self):
        self.receiving = False

    # Manda uma mensagem para um peer especifico
    def sendMessage(self, senderAddress, senderPort, clock, type, receiverAddress, receiverPort):
        message = f"{senderAddress}:{senderPort} {clock} {type}"
        print(f"Encaminhando mensagem \"{message}\" para {receiverAddress}:{receiverPort}")
        try:
            senderSocket = socket.socket()
            senderSocket.connect((receiverAddress, receiverPort))
            senderSocket.send(message.encode())
            senderSocket.close()
        except ConnectionRefusedError:
            return

    # Funcao principal!!
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

        # INICIALIZA AS ESTATISTICAS
        self.downloadStatistics = []

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