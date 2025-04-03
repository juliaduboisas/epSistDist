import socket
import sys
import threading

import commandHandler
import aux

def receiveConnections(socket):
    print(f"Connection receiver initialized on socket {socket}")
    while True:
        socket.listen()
        # se pegar uma conexão, passar para uma outra porta de socket? e manter a escolhida
        # aberta para conexões (eu ACHO)

def connectedSocket(socket):
    handler = commandHandler.CommandHandler()
    while True:
        command = socket.receive().decode()
        handler.handleRemoteCommand(command)

def eachare():
    # RECEBENDO O INPUT DA LINHA DE COMANDO
    aux.checkInputArguments(sys.argv)
    address = sys.argv[1].split(":")[0]
    port = int(sys.argv[1].split(":")[1])
    neighboursFile = sys.argv[2]
    directory = sys.argv[3]

    # COLOCANDO NO SOCKET
    peerSocket = socket.socket()
    peerSocket.bind((address, port))

    # CRIANDO A THREAD DE CONEXÕES
    # essa thread mantém o socket aberto para escutar novas conexões
    # e, quando recebe uma nova conexão, a passa para uma nova porta
    # e inicia uma nova thread de comunicação
    receiveConnectionsThread = threading.Thread(target=receiveConnections, args=(peerSocket,))
    receiveConnectionsThread.start()

    # INSTANCIANDO O COMMAND HANDLER
    handler = commandHandler.CommandHandler()

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
                      "\t[9] Sair\n")

    # INICIO DA EXECUCAO DO PROGRAMA
    print(commandOptions)
    command = input("> ")

if __name__ == '__main__':
    eachare()