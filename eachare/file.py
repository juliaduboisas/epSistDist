import os

class file():
    filename: str
    size: int
    peerIP: str
    peerPort: int
    # Additions for EP3
    duplicated: bool
    printed: bool

    def __init__(self, filename: str, size: int, peerIP: str, peerPort: int, duplicated: bool):
        self.filename = filename
        self.size = size
        self.peerIP = peerIP
        self.peerPort = peerPort
        self.duplicated = duplicated
        self.printed = False
        print(f"[DEBUG] NEW FILE \nName: {self.filename}\nSize: {self.size}\nPeer IP: {self.peerIP}\nPeer Port: {self.peerPort}\nDuplicated: {self.duplicated}")

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

    def getDuplicated(self):
        return self.duplicated

    def setDuplicatedTrue(self):
        self.duplicated = True

    def setDuplicatedFalse(self):
        self.duplicated = False

    def getPrinted(self):
        return self.printed

    def setPrintedTrue(self):
        self.printed = True

    def setPrintedFalse(self):
        self.printed = False
