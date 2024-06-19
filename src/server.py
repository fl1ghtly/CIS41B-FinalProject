import socket
import threading
import pickle
import actionIDs
from database import Database

HOST = 'localhost'
PORT = 5553
TIMEOUT = 5

class Server:
    def __init__(self) -> None:
        self._serverSocket = self.startServer()
        self._lock = threading.Lock()
        self._clients: dict[int, socket.socket] = {}
        
        while True:
            (clientSocket, address) = self._serverSocket.accept()
            print(f'New Connection at address: {address}')

            self.serveClient(clientSocket)

    def startServer(self) -> socket.socket:
        server = socket.socket()
        server.bind((HOST, PORT))
        print(f'Server online at hostname: {HOST}, port: {PORT}')
        server.listen()

        return server
        
    def sendNewMessages(self, userID: int, lastPollTime: float) -> None:
        messages = Database.getMessages(lastPollTime)
        self.sendResponse(userID, actionIDs.REQUEST_MESSAGE_UPDATE, messages)

    def sendProfiles(self, userID: int) -> None:
        profiles = Database.getProfiles()
        self.sendResponse(userID, actionIDs.REQUEST_PROFILE_UPDATE, profiles)

    def handleReceiveMessage(self, message: tuple) -> None:
        Database.saveMessage(*message)

    def handleConversationVisibility(self, channelID: int, user1Visibility: bool = None, user2Visibility: bool = None) -> None:
        pass

    def handleProfileUpdate(self, userID: int, name: str) -> None:
        pass

    def handleLogin(self, username: str, password: str) -> int | None:
        '''Validates login and returns a user id if valid or none if not'''
        return Database.handleLogin(username, password)

    def handleRegistration(self, username:str, password: str) -> None:
        pass

    def handleOpenConversation(self) -> None:
        pass

    def handleAddConversation(self) -> None:
        pass

    def getResponse(self, connection: socket.socket, size: int, timeout: float) -> bytes:
        data = b''
        connection.settimeout(timeout)
        while True:
            try:
                byte = connection.recv(size)
                if not byte:
                    break
                data += byte
            except socket.timeout:    # stop asking for data when server stops responding
                break
            
        return data

    def sendResponse(self, userID: int, actionID: int = None, *args,) -> None:
        data = {'actionID': actionID, 'data': [*args]}
        byte = pickle.dumps(data)
        connection = self._clients[userID]
        connection.sendall(byte)

    def serveClient(self, connection: socket.socket) -> None:
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
        requiresSending = {
            actionIDs.LOGIN: False, 
            actionIDs.OPEN_PAST_CONVERSATION: False,
            actionIDs.REMOVE_CONVERSATION: False, 
            actionIDs.UPDATE_PROFILE: False,
            actionIDs.ADD_CONVERSATION: False, 
            actionIDs.REGISTER: False,
            actionIDs.SENT_MESSAGE: False,
            actionIDs.REQUEST_MESSAGE_UPDATE: True,
            actionIDs.REQUEST_PROFILE_UPDATE: True}
        
        
        while True:
            # NOTE all responses sent to and from the server will be dictionaries
            response = pickle.loads(self.getResponse(connection, 4096, 0.25))
            actionID: int = response['actionID']
            userID: int = response['userID']
            data: list = response['data']

            if requiresSending[actionID]:
                returnValue = actions[actionID](userID, *data)
            else:
                returnValue = actions[actionID](*data)
            
            if actionID == actionIDs.LOGIN:
                with self._lock:
                    self._clients[returnValue] = connection