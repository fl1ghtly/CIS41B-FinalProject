import socket


def pastConvo(userId: int) -> list:
    pass

def hideConvo(userId: int, channelId: int) -> None:
    pass

def newConvo(userId: int) -> None:
    pass

def updateNick(userId: int, userNick: str) -> None:
    pass

def sendMessage(userId: int, channelId: int) -> None:
    pass

def getConvos(userId: int) -> list:
    pass

def serveClient(conn: socket.socket, userId: int) -> None:
    pass