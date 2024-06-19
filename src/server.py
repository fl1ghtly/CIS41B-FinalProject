import socket
import threading
import pickle
import actionIDs

HOST = 'localhost'
PORT = 5553
TIMEOUT = 5

def sendStoredMessages(connection: socket.socket, channelID: int, amount=50) -> None:
    # call sendMessage amount times
    pass

def sendProfiles(connection: socket.socket) -> None:
    pass

def sendMessage(connection: socket.socket, message: tuple) -> None:
    pass

def handleReceiveMessage(message: tuple) -> None:
    userID: int = message[0]
    text: str = message[1]
    timestamp: float = message[2]
    channelID: int = message[3]
    # TODO call database save message func
    # TODO send message to second user

def handleConversationVisibility(channelID: int, user1Visibility: bool = None, user2Visibility: bool = None) -> None:
    pass

def handleProfileUpdate(userID: int, name: str) -> None:
    pass

def handleLogin(username: str, password: str) -> int | None:
    '''Validates login and returns a user id if valid or none if not'''
    pass

def handleRegistration(username:str, password: str) -> None:
    pass

def handleOpenConversation() -> None:
    pass

def handleAddConversation() -> None:
    pass

def getResponse(connection: socket.socket, size: int, timeout: float) -> bytes:
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

def sendResponse(connnection: socket.socket, *args) -> None:
    data = {'data': [*args]}
    byte = pickle.dumps(data)
    connnection.sendall(byte)

def serveClient(connection: socket.socket) -> None:
    # Client sends a message declaring what action they will take
    # Handle actions from the client
    actions = {actionIDs.LOGIN: handleLogin, 
               actionIDs.OPEN_PAST_CONVERSATION: handleOpenConversation,
               actionIDs.REMOVE_CONVERSATION: handleConversationVisibility, 
               actionIDs.UPDATE_PROFILE: handleProfileUpdate,
               actionIDs.ADD_CONVERSATION: handleAddConversation, 
               actionIDs.REGISTER: handleRegistration,
               actionIDs.SENT_MESSAGE: handleReceiveMessage,
               actionIDs.REQUEST_MESSAGE_UPDATE: sendStoredMessages,
               actionIDs.REQUEST_PROFILE_UPDATE: sendProfiles}
    
    while True:
        # NOTE all responses sent to and from the server will be dictionaries
        response = pickle.loads(getResponse(connection, 4096, 0.25))
        actionID: int = response['actionID']
        data: list = response['data']

        returnValue = actions[actionID](*data)
        
        
        
if __name__ == '__main__':
    with socket.socket() as s:
        s.bind((HOST, PORT))
        print(f'Server online at hostname: {HOST}, port: {PORT}')

        s.listen()
        
        while True:
            (clientSocket, address) = s.accept()
            print(f'New Connection at address: {address}')

            serveClient(clientSocket)
            

