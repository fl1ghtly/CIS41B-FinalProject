import socket
import pickle

HEADER_SIZE = 4

# ActionIDs
LOGIN = 0
OPEN_PAST_CONVERSATION = 1
REMOVE_CONVERSATION = 2
UPDATE_PROFILE = 3
ADD_CONVERSATION = 4
REGISTER = 5
SENT_MESSAGE = 6
REQUEST_MESSAGE_UPDATE = 7
REQUEST_PROFILE_UPDATE = 8
REQUEST_USERNAMES = 9
REQUEST_CHANNELID = 10
REQUEST_USERID = 11
REQUEST_LAST_LOGIN = 12
UPDATE_LAST_LOGIN = 13

def getResponse(connection: socket.socket) -> dict | None:
    '''Gets data from a socket'''
    try:
        # Get the message size from the header
        messageSize = int.from_bytes(connection.recv(HEADER_SIZE), 'little')
        byte = connection.recv(messageSize)

        # Check if socket disconnected
        if not byte:
            return None
        
        data: dict = pickle.loads(byte)
        return data
    except ConnectionResetError:
        # Socket disconnected so return None
        return None

def sendResponse(connection: socket.socket, actionID: int = None, *args) -> bool:
    '''Sends a response to a socket. Returns whether data was sent successfully'''
    try:
        data = {'actionID': actionID, 'data': [*args]}
        byte = pickle.dumps(data)

        # Send the message header first
        header = len(byte).to_bytes(HEADER_SIZE, 'little')
        connection.sendall(header)
        # Send the message itself
        connection.sendall(byte)
        return True
    except (ConnectionResetError, ConnectionAbortedError):
        return False