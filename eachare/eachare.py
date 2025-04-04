import socket
import sys
import threading

import commandHandler as ch
import inputArgumentsChecker as argChecker
import peer as p

class eachare():

    peerSocket: socket.socket()
    handler: ch.commandHandler
    openListening: bool

    def receiveConnections(self):
        print(f"[DEBUG] Socket {self.peerSocket} ouvindo.")
        while self.openListening:
            self.peerSocket.listen()
            # se pegar uma conexão, passar para uma outra porta de socket? e manter a escolhida
            # aberta para conexões (eu ACHO)

    def receiveCommands(self):
        print(f"[DEBUG] Socket {self.peerSocket} existente para mandar comandos.")

    def startProgram(self):
        # RECEBENDO O INPUT DA LINHA DE COMANDO
        inputCheck = argChecker.inputArgumentsChecker(sys.argv)
        inputCheck.checkAll()
        address = sys.argv[1].split(":")[0]
        port = int(sys.argv[1].split(":")[1])
        neighboursFile = sys.argv[2]
        directory = sys.argv[3]
        print("[DEBUG] Argumentos separados no programa principal.")

        # COLOCANDO NO SOCKET
        self.peerSocket = socket.socket()
        self.peerSocket.bind((address, port))
        print("[DEBUG] Socket criado.")

        # CRIANDO A THREAD DE CONEXÕES
        # essa thread mantém o socket aberto para escutar novas conexões
        # e, quando recebe uma nova conexão, a passa para uma nova porta
        # e inicia uma nova thread de comunicação
        print(f"[DEBUG] Iniciando thread de listen no socket {self.peerSocket}.")
        self.openListening = True
        receiveConnectionsThread = threading.Thread(target=self.receiveConnections, args=())
        receiveConnectionsThread.start()
        print("[DEBUG] Thread de listen criada.")

        # CRIANDO A THREAD DE COMANDOS
        # essa thread recebe os comandos do usuário
        print(f"[DEBUG] Iniciando thread de comandos.")
        receiveCommandsThread = threading.Thread(target=self.receiveCommands(), args=())
        receiveCommandsThread.start()
        print("[DEBUG] Thread de comandos criada.")


        # INSTANCIANDO O COMMAND HANDLER

        # INICIANDO RELOGIO LOCAL
        # funcionamento do relogio local
        # - antes de enviar uma mensagem, incrementa o clock em 1
        # - ao receber uma mensagem, incrementa o clock em 1
        # - Sempre que o valor do relógio for atualizado, uma mensagem deverá ser exibida na
        #   saída padrão com o seguinte formato: "=> Atualizando relogio para <valor>"

        # inicia o clock do peer
        localClock = 0

        # MENSAGENS PARA IMPRIMIR
        commandOptions = ("Escolha um comando:\n" +
                          "\t[1] Listar peers\n" +
                          "\t[2] Obter peers\n" +
                          "\t[3] Listar arquivos locais\n" +
                          "\t[4] Buscar arquivos\n" +
                          "\t[5] Exibir estatisticas\n" +
                          "\t[6] Alterar tamanho de chunk\n" +
                          "\t[9] Sair")

        # INICIO DA EXECUCAO DO PROGRAMA
        while True:
            print(commandOptions)
            command = input("> ")


if __name__ == '__main__':
    eachare = eachare()
    eachare.startProgram()