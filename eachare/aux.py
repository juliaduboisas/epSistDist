import sys
import os

def checkInputArguments(args):
    # deve checar:
    # - numero de argumentos recebido
    # - se a porta indicada pode ser usada
    # - se o arquivo de vizinhos existe e possui uma porta para cada endereço?
    # - se o diretorio compartilhado existe

    # NUMERO DE ARGUMENTOS
    if(len(args) != 4): sys.exit(f"A entrada deve ser:\neachare.py <endereco>:<porta> <vizinhos.txt> <diretorio_compartilhado>")

    address = sys.argv[1].split(":")[0]
    port = int(sys.argv[1].split(":")[1])
    neighbours = sys.argv[2]
    directory = sys.argv[3]

    # CHECAGEM DA PORTA
    if(port<1024): sys.exit(f"Porta {port} reservada, selecione outra porta.")

    # CHECAGEM DA EXISTÊNCIA ARQUIVO DE VIZINHOS
    if(not(os.path.isfile(neighbours))):
        sys.exit(f"{neighbours} não é um arquivo válido, selecione um arquivo .txt válido.")
    elif(neighbours.endswith(".txt")):
        sys.exit(f"{neighbours} não é um arquivo .txt, selecione um arquivo .txt válido.")

    # CHECAGEM DO DIRETORIO
    if(not(os.path.isdir(directory))):
        sys.exit(f"{directory} não existe ou não é um diretório, selecione um diretório existente.")

    # CHECAGEM DO INTERIOR DO ARQUIVO DE VIZINHOS
    # formato esperado: endereço:porta
    f = open("vizinhos.txt", "r")
    print(f.read())
