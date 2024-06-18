import socket
import threading
import pickle
import actionIDs

def sendOnlineClients():
    pass

def sendStoredMessages(connection: socket.socket, channelID: int, amount=50) -> None:
    # call sendMessage amount times
    pass

def sendMessage(connection: socket.socket, channelID: int) -> None:
    pass

def saveMessage(message: tuple) -> None:
    pass

def receiveMessage(message: tuple, otherConnection: socket.socket) -> None:
    pass

def changeConversationVisibility(channelID: int, user1Visibility: bool = None, user2Visibility: bool = None) -> None:
    pass

def updateProfile(userID: int, name: str) -> None:
    pass

def handleLogin(username: str, password: str) -> int | None:
    '''Validates login and returns a user id if valid or none if not'''
    pass

def serveClient(connection: socket.socket) -> None:
    # Client sends a message declaring what action they will take
    # Handle action
    pass

if __name__ == '__main__':
    with socket.socket() as s:
        pass
