class DownloadStats:
    chunkSize: int
    numPeers: int
    fileSize: int
    downloadTime: int

    def __init__(self, chunkSize, numPeers, fileSize, downloadTime):
        self.chunkSize = chunkSize
        self.numPeers = numPeers
        self.fileSize = fileSize
        self.downloadTime = downloadTime
