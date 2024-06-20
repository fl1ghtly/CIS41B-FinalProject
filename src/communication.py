import socket
import pickle

HEADER_SIZE = 4

def getResponse(connection: socket.socket) -> dict | None:
    messageSize = int.from_bytes(connection.recv(HEADER_SIZE), 'little')
    byte = connection.recv(messageSize)

    # Check if socket disconnected
    if not byte:
        return None
    
    data: dict = pickle.loads(byte)
    return data

def _sendHeader(connection: socket.socket, messageSize: int) -> None:
    toSend = messageSize.to_bytes(HEADER_SIZE, 'little')
    connection.sendall(toSend)

def sendResponse(connection: socket.socket, actionID: int = None, *args) -> None:
    data = {'actionID': actionID, 'data': [*args]}
    byte = pickle.dumps(data)

    _sendHeader(connection, len(byte))
    # TODO set in try except statement
    connection.sendall(byte)