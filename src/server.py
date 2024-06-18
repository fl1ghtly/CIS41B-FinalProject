import socket
import threading
import pickle
import actionIDs

HOST = 'localhost'
PORT = 5553
TIMEOUT = 5

def sendStoredMessages(connection: socket.socket, channelID: int, amount=50) -> None:
    # call sendMessage amount times
    pass

def sendMessage(connection: socket.socket, channelID: int) -> None:
    pass

def saveMessage(message: tuple) -> None:
    pass

def receiveMessage(otherConnection: socket.socket, message: tuple) -> None:
    pass

def changeConversationVisibility(channelID: int, user1Visibility: bool = None, user2Visibility: bool = None) -> None:
    pass

def updateProfile(userID: int, name: str) -> None:
    pass

def handleLogin(username: str, password: str) -> int | None:
    '''Validates login and returns a user id if valid or none if not'''
    pass

def registerNewUser(username:str, password: str) -> None:
    pass

def getResponse(connection: socket.socket, size: int, timeout) -> bytes:
    data = b''
    connection.settimeout(timeout)
    while True:
        try:
            byte = connection.recv(size)
            if not byte:
                break
            data += byte
        except socket.timeout:    # stop asking for data when server stops responding
            break
        
    return data
    

def serveClient(connection: socket.socket) -> None:
    # Client sends a message declaring what action they will take
    # Handle action
    while True:
        response = pickle.loads(getResponse(connection, 4096, 0.25))
        
if __name__ == '__main__':
    with socket.socket() as s:
        s.bind((HOST, PORT))
        print(f'Server online at hostname: {HOST}, port: {PORT}')

        s.listen()
        
        while True:
            (clientSocket, address) = s.accept()
            print(f'New Connection at address: {address}')

            serveClient(clientSocket)
            

