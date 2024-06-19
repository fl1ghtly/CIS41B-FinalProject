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
        data = {'actionID': actionID, 'userID': self._userID, 'data': [*args]}
        bytes = pickle.dumps(data)
        self._server.sendall(bytes)
        
        response: dict = pickle.loads(self.getResponse(4096, 0.25))
        return response
        
    def getResponse(self, size: int, timeout: float) -> bytes:
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

    def login(self, username: str, password: str) -> int | None:
        '''Logs into an account and returns the user id'''
        response = self.sendAction(actionIDs.LOGIN, username, password)
        id: int = response['data']
        
        return id
        
    def receiveMessages(self, lastPollTime: float) -> list[tuple]:
        response = self.sendAction(actionIDs.REQUEST_MESSAGE_UPDATE, lastPollTime)
        # TODO check if the returned response is the correct one
        messages: list[tuple] = response['data']
        return messages
    
    def receiveProfileUpdates(self) -> list[tuple]:
        '''Returns a list all profiles'''
        response = self.sendAction(actionIDs.REQUEST_PROFILE_UPDATE)
        profileData: list[tuple] = response['data']
        return profileData
    
    def sendMessage(self, message: str, channelID: int) -> None:
        self.sendAction(actionIDs.SENT_MESSAGE, (self._userID, message, time.time(), channelID))

    def addConversation(self, otherUser: str) -> None:
        self.sendAction(actionIDs.ADD_CONVERSATION, self._userID, otherUser)