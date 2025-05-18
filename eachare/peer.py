class peer():
    address: str()
    port: int()
    status: bool
    neighbourPeers: []
    clock: int()

    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.neighbourPeers = []
        self.clock = 0

    def __str__(self):
        return f"{self.address}:{self.port} {"ONLINE" if self.status else "OFFLINE"}"

    def setAddress(self, address: str):
        self.address = address

    def getAddress(self):
        return self.address

    def setPort(self, port: int):
        self.port = port

    def getPort(self):
        return self.port

    # funcionamento do relogio local
    # - antes de enviar uma mensagem, incrementa o clock em 1
    # - ao receber uma mensagem, incrementa o clock em 1
    # - sempre que o valor do relógio for atualizado, uma mensagem deverá ser exibida na
    #   saída padrão com o seguinte formato: "=> Atualizando relogio para <valor>"
    # - se o clock de uma mensagem recebida for maior que o local, atualizar o local
    #   o maior entre os dois
    def getClock(self):
        return self.clock

    def increaseClock(self):
        self.clock += 1
        print(f"=> Atualizando relogio para {self.clock}")

    def updateClock(self, newClock: int):
        self.clock = newClock
        print(f"=> Atualizando relogio para {self.clock}")

    def setStatusOnline(self):
        self.status = True

    def setStatusOffline(self):
        self.status = False

    def getStatus(self):
        return self.status

    def setNeighbourPeers(self, neighbourPeers):
        self.neighbourPeers = neighbourPeers

    def getNeighbourPeers(self):
        return self.neighbourPeers

    def addNeighbour(self, neighbour):
        self.neighbourPeers.append(neighbour)

    def makeNeighbourList(self, vizinhos):
        f = open(vizinhos, 'r')
        for line in f:
            ip = line.split(":")[0]
            port = int(line.split(":")[1])
            newPeer = peer(ip, int(port))
            newPeer.setStatusOffline()
            self.addNeighbour(newPeer)

        for neighbour in self.neighbourPeers:
            print(f"Adicionado novo peer {neighbour.getAddress()}:{neighbour.getPort()} status {"ONLINE" if neighbour.getStatus() else "OFFLINE"}")