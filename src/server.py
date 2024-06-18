import socket
import threading
import pickle
import sqlite3

def checkOnlineClients() -> list[int]:
    pass

def sendStoredMessages(connection: socket.socket, channelID: int, amount=50) -> None:
    pass

def sendMessage(connection: socket.socket, channelID: int) -> None:
    pass

def saveMessage(message: tuple) -> None:
    pass

def changeConversationVisibility(channelID: int, user1Visibility: bool = None, user2Visibility: bool = None) -> None:
    pass

def updateProfile(userID: int, name: str) -> None:
    pass

def serveClient(connection: socket.socket) -> None:
    # Client sends a message declaring what action they will take
    # Handle action
    pass

if __name__ == '__main__':
    with socket.socket() as s:
        pass
