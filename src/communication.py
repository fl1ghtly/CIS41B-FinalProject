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

def getResponse(connection: socket.socket) -> dict | None:
    '''Gets data from a socket'''
    # Get the message size from the header
    messageSize = int.from_bytes(connection.recv(HEADER_SIZE), 'little')
    byte = connection.recv(messageSize)

    # Check if socket disconnected
    if not byte:
        return None
    
    data: dict = pickle.loads(byte)
    return data

def _sendHeader(connection: socket.socket, messageSize: int) -> None:
    '''Sends a message header to defines the size of the message'''
    toSend = messageSize.to_bytes(HEADER_SIZE, 'little')
    connection.sendall(toSend)

def sendResponse(connection: socket.socket, actionID: int = None, *args) -> None:
    '''Sends a response to a socket'''
    data = {'actionID': actionID, 'data': [*args]}
    byte = pickle.dumps(data)

    _sendHeader(connection, len(byte))
    # TODO set in try except statement
    connection.sendall(byte)