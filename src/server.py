import socket
import threading
from database import Database
import communication
import time

HOST = 'localhost'
PORT = 5553

class Server:
    def __init__(self) -> None:
        self._serverSocket = self._startServer()
        self._lock = threading.Lock()
        self._clients: dict[socket.socket, int] = {}
        self._threads: list[threading.Thread] = []
        
        while True:
            (clientSocket, address) = self._serverSocket.accept()
            print(f'New Connection at address: {address}')
            thread = threading.Thread(target=self.serveClient, args=(clientSocket, ))
            self._threads.append(thread)
            thread.start()

    def _startServer(self) -> socket.socket:
        '''Start a server socket and have it listen. Returns the socket'''
        server = socket.socket()
        server.bind((HOST, PORT))
        print(f'Server online at hostname: {HOST}, port: {PORT}')
        server.listen()

        return server
    
    def endServer(self) -> None:
        '''Closes the server and saves any changes made to the database'''
        with self._lock:
            Database.onServerClose()

        for thread in self._threads:
            thread.join()

        self._serverSocket.close()
        
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
    
    def handleOpenConversation(self, channelID: int) -> list[tuple[str, float]]:
        '''Return all messages in a channel'''
        return Database.getChannelMessages(channelID)

    def handleAddConversation(self, user1ID: int, user2Name: str) -> None:
        '''Create a new conversation between two users'''
        user2ID = Database.getUserID(user2Name)

        Database.addConversation(user1ID, user2ID)

    def sendUsernames(self, userID: int) -> dict[str:int]:
        '''Returns the list of usernames and user ids the given userID has conversed with'''
        return Database.getUsernames(userID)
    
    def sendChannelID(self, user1ID: int, user2ID: int) -> int:
        '''Returns the channelID that matches with user1ID and user2ID'''
        return Database.getChannelID(user1ID, user2ID)
    
    def sendUserID(self, username: str) -> int | None:
        '''Returns the corresponding userID given the username'''
        return Database.getUserID(username)
    
    def handleClientDisconnect(self, connection: socket.socket) -> None:
        try:
            userID = self._clients[connection]
        except KeyError:
            
            return
        print(f'Client #{userID} has disconnected')
        # TODO call the database function to set the time

    def serveClient(self, connection: socket.socket) -> None:
        '''Handle a client's requests'''
        # Client sends a message declaring what action they will take
        # Handle actions from the client
        actions = {
            communication.LOGIN: self.handleLogin, 
            communication.OPEN_PAST_CONVERSATION: self.handleOpenConversation,
            communication.REMOVE_CONVERSATION: self.handleConversationVisibility, 
            communication.UPDATE_PROFILE: self.handleProfileUpdate,
            communication.ADD_CONVERSATION: self.handleAddConversation, 
            communication.REGISTER: self.handleRegistration,
            communication.SENT_MESSAGE: self.handleReceiveMessage,
            communication.REQUEST_MESSAGE_UPDATE: self.sendNewMessages,
            communication.REQUEST_PROFILE_UPDATE: self.sendProfiles,
            communication.REQUEST_USERNAMES: self.sendUsernames,
            communication.REQUEST_USERID: self.sendUserID}
        
        while True:
            # NOTE all responses sent to and from the server will be dictionaries
            response = communication.getResponse(connection)

            if not response:
                self.handleClientDisconnect(connection)
                break
            
            actionID: int = response['actionID']
            data: list = response['data']

            with self._lock:
                returnValue = actions[actionID](*data)
            
            if actionID == communication.LOGIN:
                with self._lock:
                    self._clients[connection] = returnValue
                 
            communication.sendResponse(connection, actionID, returnValue)
            
if __name__ == '__main__':
    try:
        server = Server()
    finally:
        server.endServer()