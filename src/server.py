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
        self._clients = {}
        
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
        
    def sendStoredMessages(self, connection: socket.socket, channelID: int, max=200) -> None:
        # call sendMessage amount times
        pass

    def sendProfiles(self, connection: socket.socket) -> None:
        pass

    def sendMessage(self, connection: socket.socket, message: tuple) -> None:
        pass

    def handleReceiveMessage(self, message: tuple) -> None:
        userID: int = message[0]
        text: str = message[1]
        timestamp: float = message[2]
        channelID: int = message[3]

        Database.saveMessage(userID, text, timestamp, channelID)

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

    def sendResponse(self, connnection: socket.socket, *args) -> None:
        data = {'data': [*args]}
        byte = pickle.dumps(data)
        connnection.sendall(byte)

    def serveClient(self, connection: socket.socket) -> None:
        # Client sends a message declaring what action they will take
        # Handle actions from the client
        actions = {actionIDs.LOGIN: self.handleLogin, 
                   actionIDs.OPEN_PAST_CONVERSATION: self.handleOpenConversation,
                   actionIDs.REMOVE_CONVERSATION: self.handleConversationVisibility, 
                   actionIDs.UPDATE_PROFILE: self.handleProfileUpdate,
                   actionIDs.ADD_CONVERSATION: self.handleAddConversation, 
                   actionIDs.REGISTER: self.handleRegistration,
                   actionIDs.SENT_MESSAGE: self.handleReceiveMessage,
                   actionIDs.REQUEST_MESSAGE_UPDATE: self.sendStoredMessages,
                   actionIDs.REQUEST_PROFILE_UPDATE: self.sendProfiles}
        
        while True:
            # NOTE all responses sent to and from the server will be dictionaries
            response = pickle.loads(self.getResponse(connection, 4096, 0.25))
            actionID: int = response['actionID']
            data: list = response['data']

            returnValue = actions[actionID](*data)
            
            if actionID == actionIDs.LOGIN:
                with self._lock:
                    self._clients[returnValue] = connection
        
'''
if __name__ == '__main__':
    with socket.socket() as s:
        s.bind((HOST, PORT))
        print(f'Server online at hostname: {HOST}, port: {PORT}')

        s.listen()
        
        while True:
            (clientSocket, address) = s.accept()
            print(f'New Connection at address: {address}')

            serveClient(clientSocket)
'''
            

