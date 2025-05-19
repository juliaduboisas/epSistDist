import os

class file():
    filename: str
    size: int
    peerIP: str
    peerPort: int

    def __init__(self, filename: str, size: int, peerIP: str, peerPort: int):
        self.filename = filename
        self.size = size
        self.peerIP = peerIP
        self.peerPort = peerPort
        print(f"[DEBUG] NEW FILE \nName: {self.filename}\nSize: {self.size}\nPeer IP: {self.peerIP}\nPeer Port: {self.peerPort}")

    def __str__(self):
        return f"{self.filename} {self.size} {self.peerIP}:{self.peerPort}"

    def getFilename(self):
        return self.filename

    def setFilename(self, filename):
        self.filename = filename

    def getSize(self):
        return self.size

    def setSize(self, size):
        self.size = size

    def getPeerIP(self):
        return self.peerIP

    def setPeerIP(self, ip):
        self.peerIP = ip

    def getPeerPort(self):
        return self.peerPort

    def setPeerPort(self, port):
        self.peerPort = port