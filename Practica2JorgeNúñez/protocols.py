import struct
import json

MSG_JOIN = "MSG_JOIN"
MSG_WELCOME = "MSG_WELCOME"
MSG_YOUR_TURN = "MSG_YOUR_TURN"
MSG_SEND_SERVER_OPTION = "MSG_SEND_SERVER_OPTION"
MSG_SEND_GAMES = "MSG_SEND_GAMES"
SEND_GAMES_CHOICE = "SEND_GAMES_CHOICE"
SEND_VALID_GAME = "SEND_VALID_GAME"
MOVE = "MOVE"
VALID_MOVE = "VALID_MOVE"
SERVER_MESSAGE = "SERVER_MESSAGE"
SEND_END_GAME = "SEND_END_GAME"
SEND_DC_ME = "SEND_DC_ME"
SEND_DC_SERVER = "SEND_DC_SERVER"

class InvalidProtocol(Exception):
    def __init__(self):
        super().__init__("Unknown message received")

class ConnectionClosed(Exception):
    def __init__(self):
        super().__init__("Connection closed by other")

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf
def send_one_message(sock, data):
    try:
        encoded_data = json.dumps(data).encode()
        length = len(encoded_data)
        header = struct.pack("!I", length)
        sock.sendall(header)
        sock.sendall(encoded_data)
    except BrokenPipeError:
        print("The server is disconnected")
def recv_one_message(sock):
    header_buffer = recvall(sock, 4)
    if header_buffer:
        header = struct.unpack("!I", header_buffer)
        length = header[0]
        encoded_data = recvall(sock, length)
        message = json.loads(encoded_data.decode())
        return message
    else:
        raise ConnectionResetError()


