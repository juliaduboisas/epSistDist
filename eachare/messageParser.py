class messageParser():
    # gramatica da mensagem:
    # <ORIGEM> <CLOCK> <TIPO>[ ARGUMENTO1 ARGUMENTO2...]\n

    msg: ""
    senderIP: ""
    senderPort: int
    senderClock: int
    messageType: ""

    def parse(self, message):
        self.senderIP = message.split(" ")[0].split(":")[0]
        self.senderPort = int(message.split(" ")[0].split(":")[1])
        self.senderClock = int(message.split(" ")[1])  # esse clock no momento é local, mas imagino que futuramente virará global
        self.messageType = message.split(" ")[2]


