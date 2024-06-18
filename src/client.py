import socket
import pickle
import time
import actionIDs

HOST = '127.0.0.1'
PORT = 5553

class Client:
    def __init__(self, username: str, password: str) -> None:
        self._server = self.connect()
        self._userID = self.login(username, password)
    
    def connect(self) -> socket.socket:
        server = socket.socket()
        server.connect((HOST, PORT))

        return server
    
    def disconnect(self) -> None:
        self._server.close()
    
    def sendAction(self, actionID: int, *args) -> None:
        data = {'actionID': actionID, 'data': [*args]}
        bytes = pickle.dumps(data)
        self._server.sendall(bytes)

    def login(self, username: str, password: str) -> int:
        '''Logs into an account and returns the user id'''
        pass
        
    def receiveMessages(self) -> list[tuple]:
        pass
    
    def receiveProfileUpdates(self) -> list[tuple]:
        pass