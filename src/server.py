import socket
import threading
import time
from database import Database
import communication

HOST = 'localhost'
PORT = 5553

class Server:
    def __init__(self) -> None:
        self._serverSocket: socket.socket = None
        self._lock = threading.Lock()
        self._clients: dict[socket.socket, int] = {}

    def _run(self) -> None:
        '''Accept and handle new client connections'''
        while True:
            (clientSocket, address) = self._serverSocket.accept()
            print(f'New Connection at address: {address}')
            thread = threading.Thread(target=self.serveClient, args=(clientSocket,))
            thread.start()
        
    def startServer(self) -> None:
        '''Start a server socket and have it listen. Returns the socket'''
        self._serverSocket = socket.socket()
        self._serverSocket.bind((HOST, PORT))
        print(f'Server online at hostname: {HOST}, port: {PORT}')
        self._serverSocket.listen()

        daemon = threading.Thread(target=self._run, daemon=True)
        daemon.start()
        
        print('Enter q to close the server')
        while daemon.is_alive():
            key = input()
            if key.lower() == 'q':
                break
                
    def endServer(self) -> None:
        '''Closes the server and saves any changes made to the database'''
        # Set everyone's last login time 
        # NOTE Don't use self._clients.key() because it returns 
        # the view which raises an error when the dictionary 
        # is modified during handleClientDisconnect
        for connection in list(self._clients):
            self.handleClientDisconnect(connection)

        # Commit all unsaved changes to the Database
        with self._lock:
            Database.onServerClose()

        # Close the listening socket
        self._serverSocket.close()
        
    def sendNewMessages(self, channelID: int, lastPollTime: float) -> list[tuple]:
        '''Return all messages since a given time'''
        return Database.getMessages(channelID, lastPollTime)

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
    
    def handleOpenConversation(self, channelID: int) -> list[tuple[int, str]]:
        '''Return all messages in a channel'''
        return Database.getChannelMessages(channelID)

    def handleAddConversation(self, user1ID: int, user2Name: str) -> None:
        '''Create a new conversation between two users'''
        user2ID = Database.getUserID(user2Name)

        # Make sure that the users are different
        if user1ID != user2ID:
            Database.addConversation(user1ID, user2ID)

    def sendUsernames(self, userID: int) -> list[tuple[str, int]]:
        '''Returns the list of usernames and user ids the given userID has conversed with'''
        return Database.getUsernames(userID)
    
    def sendChannelID(self, user1ID: int, user2ID: int) -> int | None:
        '''Returns the channelID that matches with user1ID and user2ID'''
        # Can't have a conversation with self
        if user1ID == user2ID:
            return None
        
        return Database.getChannelID(user1ID, user2ID)
    
    def sendUserID(self, username: str) -> int | None:
        '''Returns the corresponding userID given the username'''
        return Database.getUserID(username)
    
    def sendLastLogin(self, userID: int) -> float:
        '''Returns the last login time of given userID'''
        return Database.getLastLogin(userID)
    
    def updateLastLogin(self, userID: int, lastLogin: float) -> None:
        '''Updates the last login time of given userID'''
        return Database.setLastLogin(userID, lastLogin)
    
    def sendVisibility(self, userID: int) -> list[bool]:
        '''Returns the visibility of channels of given user'''
        return Database.getVisibility(userID)
    
    def handleClientDisconnect(self, connection: socket.socket) -> None:
        # Get the user id and remove the element in the dict
        try:
            userID = self._clients.pop(connection)
        except KeyError:
            return

        print(f'Client #{userID} has disconnected')
        self.updateLastLogin(userID, time.time())
        
        # Close the client's connection if it wasn't already
        # Will also implicitly end the client thread as the socket is shutdown
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()

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
            communication.REQUEST_CHANNELID: self.sendChannelID,
            communication.REQUEST_USERID: self.sendUserID,
            communication.REQUEST_LAST_LOGIN: self.sendLastLogin,
            communication.UPDATE_LAST_LOGIN: self.updateLastLogin,
            communication.REQUEST_CHANNEL_VISIBILITY: self.sendVisibility}
        
        while True:
            # NOTE all responses sent to and from the server will be dictionaries
            response = communication.getResponse(connection)

            # Check if client disconnected
            if not response:
                self.handleClientDisconnect(connection)
                break
            
            actionID: int = response['actionID']
            data: list = response['data']

            # Do the action the client requested
            # Only let one thread read/write to the database at a time
            with self._lock:
                returnValue = actions[actionID](*data)
            
            # If client requested to login then store their userID for later
            if actionID == communication.LOGIN:
                with self._lock:
                    self._clients[connection] = returnValue
                 
            # Return the response to the client
            communication.sendResponse(connection, actionID, returnValue)

if __name__ == '__main__':
    server = Server()
    try:
        server.startServer()
    finally:
        server.endServer()