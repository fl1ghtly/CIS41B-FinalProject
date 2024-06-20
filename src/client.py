import socket
import pickle
import time
import actionIDs

HOST = '127.0.0.1'
PORT = 5553

class Client:
    HEADER_SIZE = 4
    def __init__(self) -> None:
        self._server = self._connect()
        self._userID = None
    
    def _connect(self) -> socket.socket:
        server = socket.socket()
        server.connect((HOST, PORT))
        print(f'Client connected to: {HOST}, {PORT}')

        return server
    
    def disconnect(self) -> None:
        self._server.close()
    
    def sendAction(self, actionID: int, *args) -> dict:
        data = {'actionID': actionID, 'userID': self._userID, 'data': [*args]}
        dataBytes = pickle.dumps(data)

        self.sendHeader(len(dataBytes))
        self._server.sendall(dataBytes)
        
        response: dict = pickle.loads(self.getResponse())
        return response
        
    def sendHeader(self, messageSizeBytes: int) -> None:
        toSend = messageSizeBytes.to_bytes(Client.HEADER_SIZE, 'little')
        self._server.sendall(toSend)

    def getResponse(self) -> bytes:
        messageSize = int.from_bytes(self._server.recv(Client.HEADER_SIZE), 'little')
        data = self._server.recv(messageSize)
        return data

    def login(self, username: str, password: str) -> int | None:
        '''Logs into an account and returns the user id'''
        response: dict = self.sendAction(actionIDs.LOGIN, username, password)
        id: int = response['data']
        
        return id
    
    def openConversation(self, channelID: int) -> list[tuple]:
        response: dict = self.sendAction(actionIDs.OPEN_PAST_CONVERSATION, channelID)
        return response['data']
    
    def removeConversation(self, channelID: int):
        self.sendAction(actionIDs.REMOVE_CONVERSATION, channelID, self._userID, False)
    
    def updateProfile(self, name: str) -> None:
        self.sendAction(actionIDs.UPDATE_PROFILE, self._userID, name)
        
    def addConversation(self, otherUser: str) -> None:
        self.sendAction(actionIDs.ADD_CONVERSATION, self._userID, otherUser)

    def register(self, username: str, password: str) -> bool:
        response: dict = self.sendAction(actionIDs.REGISTER, username, password)
        return response['data']
    
    def sendMessage(self, message: str, channelID: int) -> None:
        self.sendAction(actionIDs.SENT_MESSAGE, (self._userID, message, time.time(), channelID))

    def receiveMessages(self, lastPollTime: float) -> list[tuple]:
        response: dict = self.sendAction(actionIDs.REQUEST_MESSAGE_UPDATE, lastPollTime)
        # TODO check if the returned response is the correct one
        messages: list[tuple] = response['data']
        return messages
    
    def receiveProfileUpdates(self) -> list[tuple]:
        '''Returns a list all profiles'''
        response: dict = self.sendAction(actionIDs.REQUEST_PROFILE_UPDATE)
        profileData: list[tuple] = response['data']
        return profileData
    
    def getUserID(self) -> int | None:
        return self._userID

if __name__ == '__main__':
    client = Client()
    print(client.register('testing', 'password'))
    #print(client.login('testing', 'password'))
    while True:
        time.sleep(2)
        print('alive')
    
    #client.disconnect()