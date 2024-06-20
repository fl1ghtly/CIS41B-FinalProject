import socket
import time
import actionIDs
import communication

HOST = '127.0.0.1'
PORT = 5553

class Client:
    def __init__(self) -> None:
        self._server = self._connect()
        self._userID: int | None = None
    
    def _connect(self) -> socket.socket:
        '''Connect to the server and return the server's socket'''
        server = socket.socket()
        server.connect((HOST, PORT))
        print(f'Client connected to: {HOST}, {PORT}')

        return server
    
    def disconnect(self) -> None:
        '''Disconnect the client from the server'''
        self._server.close()
    
    def sendAction(self, actionID: int, *args) -> dict:
        '''Sends and receives information to the server'''
        communication.sendResponse(self._server, actionID, *args)
        response: dict = communication.getResponse(self._server)
        return response
        
    def login(self, username: str, password: str) -> int | None:
        '''Logs into an account and returns the user id if successful'''
        response: dict = self.sendAction(actionIDs.LOGIN, username, password)
        id: int = response['data']
        
        return id
    
    def openConversation(self, channelID: int) -> list[tuple]:
        '''Requests server for a channel's messages'''
        response: dict = self.sendAction(actionIDs.OPEN_PAST_CONVERSATION, channelID)
        return response['data']
    
    def removeConversation(self, channelID: int):
        '''Request server to hide a conversation'''
        self.sendAction(actionIDs.REMOVE_CONVERSATION, channelID, self._userID, False)
    
    def updateProfile(self, name: str) -> None:
        '''Request server to update user's profile'''
        self.sendAction(actionIDs.UPDATE_PROFILE, self._userID, name)
        
    def addConversation(self, otherUser: str) -> None:
        '''Request server to add a conversation with another user'''
        self.sendAction(actionIDs.ADD_CONVERSATION, self._userID, otherUser)

    def register(self, username: str, password: str) -> bool:
        '''Request server to create a new account. Returns whether
        account creation is successful'''
        response: dict = self.sendAction(actionIDs.REGISTER, username, password)
        return response['data']
    
    def sendMessage(self, message: str, channelID: int) -> None:
        '''Sends a chat message to the server'''
        self.sendAction(actionIDs.SENT_MESSAGE, (self._userID, message, time.time(), channelID))

    def receiveMessages(self, lastPollTime: float) -> list[tuple]:
        '''Receive all new messages since a certain time'''
        response: dict = self.sendAction(actionIDs.REQUEST_MESSAGE_UPDATE, lastPollTime)
        # TODO check if the returned response is the correct one
        return response['data']
    
    def receiveProfileUpdates(self) -> list[tuple]:
        '''Returns a list all profiles'''
        response: dict = self.sendAction(actionIDs.REQUEST_PROFILE_UPDATE)
        return response['data']
    
    def getUserID(self) -> int | None:
        return self._userID

if __name__ == '__main__':
    client = Client()
    print(client.register('testing', 'password'))
    print(client.login('testing', 'password'))
    
    while True:
        time.sleep(2)
        print('alive')
    
    #client.disconnect()