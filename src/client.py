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
        pass
    
    def disconnect(self) -> None:
        self._server.close()
    
    def sendMessage(self, message: str, channelID: int) -> None:
        pass

    def sendAction(self, actionID: int, *args, **kwargs) -> None:
        pass

    def login(self, username: str, password: str) -> int:
        '''Logs into an account and returns the user id'''
        pass
        
    def receiveMessages(self) -> list[tuple]:
        pass
    
    def receiveProfileUpdates(self) -> list[tuple]:
        pass