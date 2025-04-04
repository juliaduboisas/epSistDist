import sys
import os

class inputArgumentsChecker():
    # deve checar:
    # - numero de argumentos recebido
    # - se a porta indicada pode ser usada
    # - se o arquivo de vizinhos existe e possui uma porta para cada endereço?
    # - se o diretorio compartilhado existe
    args: str
    address: str
    port: int
    neighbours: str
    directory: str

    def __init__(self, args: str):
        self.args = args

    # NUMERO DE ARGUMENTOS
    def checkLength(self):
        if(len(self.args) != 4): sys.exit(f"A entrada deve ser:\neachare.py <endereco>:<porta> <vizinhos.txt> <diretorio_compartilhado>")
        print("[DEBUG] Quantidade correta de argumentos recebida.")

    def splitArguments(self):
        self.address = sys.argv[1].split(":")[0]
        self.port = int(sys.argv[1].split(":")[1])
        self.neighbours = sys.argv[2]
        self.directory = sys.argv[3]
        print("[DEBUG] Argumentos separados para a checagem.")

    # CHECAGEM DA PORTA
    def checkPort(self):
        if(self.port<1024): sys.exit(f"Porta {port} reservada, selecione outra porta.")
        print("[DEBUG] Porta selecionada aceita.")

    # CHECAGEM DO ARQUIVO DE VIZINHOS
    def checkNeighboursFile(self):
        # CHECAGEM DA EXISTENCIA DO ARQUIVO
        if(not(os.path.isfile(self.neighbours))):
            sys.exit(f"{neighbours} não é um arquivo válido, selecione um arquivo .txt válido.")
        elif(not(self.neighbours.endswith(".txt"))):
            print(self.neighbours)
            sys.exit(f"{self.neighbours} não é um arquivo .txt, selecione um arquivo .txt válido.")
        print("[DEBUG] Arquivo de vizinhos válido.")

        # CHECAGEM DO INTERIOR DO ARQUIVO DE VIZINHOS
        # acho que nem precisa na vida real

    # CHECAGEM DO DIRETORIO
    def checkDirectory(self):
        if(not(os.path.isdir(self.directory))):
            sys.exit(f"{self.directory} não existe ou não é um diretório, selecione um diretório existente.")
        print("[DEBUG] Diretório compartilhado válido.")

    def checkAll(self):
        self.checkLength()
        self.splitArguments()
        self.checkPort()
        self.checkNeighboursFile()
        self.checkDirectory()
        print("[DEBUG] Todas as checagens de argumentos completas.")

