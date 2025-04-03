import enum

class peerStatus(enum.Enum):
    OFFLINE = 0
    ONLINE = 1

class peer():
    address: string
    port: integer
    status: peerStatus

    def setAddress(self, address: string):
        self.address = address

    def getAddress(self):
        return self.address

    def setPort(self, port: int):
        self.port = port

    def getPort(self):
        return self.port

    def setStatusOnline(self):
        self.status = status.ONLINE

    def setStatusOffline(self):
        self.status = status.OFFLINE

    def getStatus(self):
        return self.status