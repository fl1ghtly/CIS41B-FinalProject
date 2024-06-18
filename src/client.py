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
    
    def sendAction(self, actionID: int, *args) -> dict:
        data = {'actionID': actionID, 'data': [*args]}
        bytes = pickle.dumps(data)
        self._server.sendall(bytes)
        
        response: dict = pickle.loads(self.getResponse(4096, 0.25))
        return response
        
    def getResponse(self, size: int, timeout: float):
        data = b''
        self._server.settimeout(timeout)
        while True:
            try:
                byte = self._server.recv(size)
                if not byte:
                    break
                data += byte
            except socket.timeout:    # stop asking for data when server stops responding
                break
            
        return data
        

    def login(self, username: str, password: str) -> int:
        '''Logs into an account and returns the user id'''
        pass
        
    def receiveMessages(self) -> list[tuple]:
        pass
    
    def receiveProfileUpdates(self) -> list[tuple]:
        pass