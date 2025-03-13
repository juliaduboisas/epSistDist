import socket
import sys

# COLOCAR AS FUNCOES EM UMA BIBLIOTECA?

def checkInputArguments(adress, port, neighbours, directory):
    # deve checar:
    # - se a porta indicada pode ser usada
    # - se o arquivo de vizinhos existe e possui uma porta para cada endereço?
    # - se o diretorio compartilhado existe

    # CHECAGEM DA PORTA
    if(port<1024): sys.exit(f"Porta {port} reservada, selecione outra porta")

    # CHECAGEM DO ARQUIVO DE VIZINHOS

    # CHECAGEM DO DIRETORIO

def commandHandler(comand):
    match command:
        case 1:
            return "HELLO"
        case _:
            return "Esse comando não é reconhecido"

def eachare():
    # linha de comando:
    # python eachare.py <endereco>:<porta> <vizinhos.txt> <diretorio_compartilhado>

    # RECEBENDO O INPUT DA LINHA DE COMANDO
    address = sys.argv[1].split(":")[0]
    port = int(sys.argv[1].split(":")[1])
    neighbours = sys.argv[2]
    directory = sys.argv[3]
    print(f"{address}, {port}, {neighbours}, {directory}")
    checkInputArguments(address, port, neighbours, directory)

    # COLOCANDO NO SOCKET
    peerSocket = socket.socket()
    peerSocket.bind((address, port))

    # INICIANDO RELOGIO LOCAL
    # funcionamento do relogio local
    # - antes de enviar uma mensagem, incrementa o clock em 1
    # - ao receber uma mensagem, incrementa o clock em 1
    # - Sempre que o valor do relógio for atualizado, uma mensagem deverá ser exibida na
    #   saída padrão com o seguinte formato: "=> Atualizando relogio para <valor>"

    # inicia o clock do peer
    localClock = 0

    # MENSAGENS PARA IMPRIMIR
    commandOptions = "Escolha um comando:\n\t[1] Listar peers\n\t[2] Obter peers\n\t[3] Listar arquivos locais\n\t[4] Buscar arquivos\n\t[5] Exibir estatisticas\n\t[6] Alterar tamanho de chunk\n\t[9] Sair\n"

    # INICIO DA EXECUCAO DO PROGRAMA
    print(commandOptions)
    command = input("> ")

if __name__ == '__main__':
    eachare()