import socket
import pickle

HEADER_SIZE = 4

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