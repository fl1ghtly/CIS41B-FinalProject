import socket
import time
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
    
    def _returnData(self, response: dict | None) -> list[tuple] | None:
        '''Return the data list of the response or None if response
        doesn't exist'''
        if not response:
            return None
        
        return response['data']
    
    def disconnect(self) -> None:
        '''Disconnect the client from the server'''
        self._server.close()
    
    def sendAction(self, actionID: int, *args) -> dict | None:
        '''Sends and receives information to the server'''
        communication.sendResponse(self._server, actionID, *args)
        # Will return None when server goes offline or can't reach the server
        response: dict | None = communication.getResponse(self._server)
        return response
        
    def login(self, username: str, password: str) -> int | None:
        '''Logs into an account and returns the user id if successful'''
        response: dict | None = self.sendAction(communication.LOGIN, username, password)

        if not response:
            return None
        
        id: int = response['data']
        
        if id:
          self._userID = id
            
        return id
    
    def openConversation(self, channelID: int) -> list[tuple[int, str, float]] | None:
        '''Requests server for a channel's messages'''
        response: dict | None = self.sendAction(communication.OPEN_PAST_CONVERSATION, channelID)
        return self._returnData(response)
    
    def removeConversation(self, channelID: int) -> None:
        '''Request server to hide a conversation'''
        self.sendAction(communication.REMOVE_CONVERSATION, channelID, self._userID, False)
    
    def updateProfile(self, name: str) -> None:
        '''Request server to update user's profile'''
        self.sendAction(communication.UPDATE_PROFILE, self._userID, name)
        
    def addConversation(self, otherUser: str) -> None:
        '''Request server to add a conversation with another user'''
        self.sendAction(communication.ADD_CONVERSATION, self._userID, otherUser)

    def register(self, username: str, password: str) -> bool | None:
        '''Request server to create a new account. Returns whether
        account creation is successful'''
        response: dict | None = self.sendAction(communication.REGISTER, username, password)

        if not response:
            return None
        # Special case of the data return where we request the bool itself rather than the
        # list containing the bool
        return response['data'][0]
    
    def sendMessage(self, message: str, channelID: int) -> None:
        '''Sends a chat message to the server'''
        self.sendAction(communication.SENT_MESSAGE, (message, self._userID, time.time(), channelID))

    def receiveMessages(self, lastPollTime: float) -> list[tuple] | None:
        '''Receive all new messages since a certain time'''
        response: dict | None = self.sendAction(communication.REQUEST_MESSAGE_UPDATE, lastPollTime)
        return self._returnData(response)
    
    def receiveProfileUpdates(self) -> list[tuple] | None:
        '''Returns a list all profiles'''
        response: dict | None = self.sendAction(communication.REQUEST_PROFILE_UPDATE)
        return self._returnData(response)
    
    def receiveUsernames(self) -> dict[str: int] | None:
        '''Receives a list of all the username and user ids the user has conversed with'''
        response: dict | None = self.sendAction(communication.REQUEST_USERNAMES, self._userID)
        return self._returnData(response)
    
    def receiveChannelID(self, user2ID: int) -> int | None:
        '''Receives a channelID that matches with self._userID and user2ID'''
        response: dict | None = self.sendAction(communication.REQUEST_CHANNELID, self._userID, user2ID)
        return self._returnData(response)
    
    def receiveUserID(self, username: str) -> int | None:
        '''Receives the corresponding userID given the username'''
        response: dict | None = self.sendAction(communication.REQUEST_USERID, username)
        return self._returnData(response)
    
    def getUserID(self) -> int | None:
        return self._userID
    
    def getLastLogin(self, userID: int) -> float | None:
        '''Receives the last login time of given userID'''
        response: dict | None = self.sendAction(communication.REQUEST_LAST_LOGIN, userID)
        return self._returnData(response)

if __name__ == '__main__':
    client = Client()
    print(client.register('testing', 'password'))
    print(client.login('testing', 'password'))
    
    while True:
        time.sleep(2)
        print('alive')
    
    #client.disconnect()