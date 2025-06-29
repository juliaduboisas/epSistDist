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
        return f"{self.address}:{self.port}:{"ONLINE" if self.status else "OFFLINE"}:{self.clock}"

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
        self.clock = newClock + 1
        print(f"=> Atualizando relogio para {self.clock}")

    def updatePeerClock(self, newClock: int):
        self.clock = newClock

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
        for n in self.neighbourPeers:
            if neighbour == n:
                return False
        self.neighbourPeers.append(neighbour)
        print(
            f"Adicionado novo peer {neighbour.getAddress()}:{neighbour.getPort()}:{neighbour.getClock()} status {"ONLINE" if neighbour.getStatus() else "OFFLINE"}")
        return True

    def makeNeighbourList(self, vizinhos):
        f = open(vizinhos, 'r')
        for line in f:
            ip = line.split(":")[0]
            port = int(line.split(":")[1])
            newPeer = peer(ip, int(port))
            newPeer.setStatusOffline()
            newPeer.updatePeerClock(0)
            self.addNeighbour(newPeer)

        for neighbour in self.neighbourPeers:
            print(f"Adicionado novo peer {neighbour.getAddress()}:{neighbour.getPort()}:{neighbour.getClock()} status {"ONLINE" if neighbour.getStatus() else "OFFLINE"}")