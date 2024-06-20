import socket
import threading
import actionIDs
from database import Database
import communication

HOST = 'localhost'
PORT = 5553

class Server:
    def __init__(self) -> None:
        self._serverSocket = self._startServer()
        self._lock = threading.Lock()
        self._clients: dict[int, socket.socket] = {}
        
        while True:
            (clientSocket, address) = self._serverSocket.accept()
            print(f'New Connection at address: {address}')

            self.serveClient(clientSocket)

    def _startServer(self) -> socket.socket:
        '''Start a server socket and have it listen. Returns the socket'''
        server = socket.socket()
        server.bind((HOST, PORT))
        print(f'Server online at hostname: {HOST}, port: {PORT}')
        server.listen()

        return server
        
    def sendNewMessages(self, lastPollTime: float) -> list[tuple]:
        '''Return all messages since a given time'''
        return Database.getMessages(lastPollTime)

    def sendProfiles(self) -> list[tuple]:
        '''Return all registered users'''
        return Database.getProfiles()

    def handleReceiveMessage(self, message: tuple) -> None:
        '''Saves a message to the database'''
        Database.saveMessage(*message)

    def handleConversationVisibility(self, channelID: int, userID: int, visibility: bool) -> None:
        '''Changes visibliity of a conversation for a user'''
        Database.hideConversation(channelID, userID, visibility)

    def handleProfileUpdate(self, userID: int, name: str) -> None:
        '''Change the profile of a user'''
        Database.changeProfile(userID, name)

    def handleLogin(self, username: str, password: str) -> int | None:
        '''Validates login and returns a user id if valid or none if not'''
        return Database.handleLogin(username, password)

    def handleRegistration(self, username: str, password: str) -> bool:
        '''Create a new account. Returns whether account creation is successful'''
        return Database.registerUser(username, password)
    
    def handleOpenConversation(self, channelID: int) -> list[tuple]:
        '''Return all messages in a channel'''
        return Database.getChannelMessages(channelID)

    def handleAddConversation(self, user1ID: int, user2Name: str) -> None:
        '''Create a new conversation between two users'''
        user2ID = Database.getUserID(user2Name)

        Database.addConversation(user1ID, user2ID)

    def serveClient(self, connection: socket.socket) -> None:
        '''Handle a client's requests'''
        # Client sends a message declaring what action they will take
        # Handle actions from the client
        actions = {
            actionIDs.LOGIN: self.handleLogin, 
            actionIDs.OPEN_PAST_CONVERSATION: self.handleOpenConversation,
            actionIDs.REMOVE_CONVERSATION: self.handleConversationVisibility, 
            actionIDs.UPDATE_PROFILE: self.handleProfileUpdate,
            actionIDs.ADD_CONVERSATION: self.handleAddConversation, 
            actionIDs.REGISTER: self.handleRegistration,
            actionIDs.SENT_MESSAGE: self.handleReceiveMessage,
            actionIDs.REQUEST_MESSAGE_UPDATE: self.sendNewMessages,
            actionIDs.REQUEST_PROFILE_UPDATE: self.sendProfiles}
        
        while True:
            # NOTE all responses sent to and from the server will be dictionaries
            response = communication.getResponse(connection)

            if not response:
                print('Client has disconnected')
                break
            
            actionID: int = response['actionID']
            data: list = response['data']

            returnValue = actions[actionID](*data)
            
            if actionID == actionIDs.LOGIN:
                with self._lock:
                    self._clients[returnValue] = connection
                 
            communication.sendResponse(connection, actionID, returnValue)
            
if __name__ == '__main__':
    server = Server()