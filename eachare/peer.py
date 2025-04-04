class peer():
    address: str()
    port: int()
    status: bool
    neighbourPeers: []

    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.neighbourPeers = []

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
            print(f"{line}")
            newPeer = peer(ip, int(port))
            newPeer.setStatusOnline()
            self.addNeighbour(newPeer)

        for x in self.neighbourPeers:
            print(f"{x}")