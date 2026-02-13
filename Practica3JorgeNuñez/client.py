import socket
import protocols as p
from args import client_parse_args, client_check_args
import getopt
stop = False

class ArgsError(Exception):
    def __init__(self, message):
        super().__init__(message)


def ask_number():
    exit = False
    n = None
    while not exit:
        try:
            n = int(input("Enter a number: "))
            exit = True
        except ValueError:
            print("Please,enter an integer number ")
    return n


def get_option(menu, range_options):
    exit = False
    option = None
    while not exit:
        print(menu)
        try:
            option = int(input("Choose an option: "))
            if option in range_options:
                exit = True
            else:
                raise ValueError
        except ValueError:
            print("Please, enter a correct integer number. ")
    return option

def read_int_option_in_options_range(message, options):
    option = None
    valid = False
    while not valid:
        print(message, end="")
        try:
            option =int(input())
            if option in options:
                valid = True
            else:
                raise ValueError
        except:
            print(f"ERROR: Invalid option. Must be a value contains in options")
        return option
def send_join(name, client_socket):
    message = {'header': p.MSG_JOIN, 'name': name}
    p.send_one_message(client_socket, message)

def send_server_option(option, client_socket):
    message = {'header': p.MSG_SEND_SERVER_OPTION, 'option': option}
    p.send_one_message(client_socket, message)

def manage_msg_welcome(message, client_socket):
    global stop
    stop = False
    accepted = message['accepted']
    msg = message['message']
    if accepted:
        option = get_option(msg, message['options_range'])
        send_server_option(option, client_socket)
    else:
        print(msg)
        stop = True
    return stop

def send_game_choice(option_game, client_socket):
    message = {'header': p.SEND_GAMES_CHOICE, 'option': option_game}
    p.send_one_message(client_socket, message)

def manage_msg_send_games(message, client_socket):
    option = read_int_option_in_options_range(message['message'], message['Options_Range'])
    send_game_choice(option, client_socket)

def manage_send_valid_game(message):
    joined = message['joined']
    reason = message['reason']
    print(reason)

def manage_server_message(message):
    print(message['message'])

def manage_your_turn(client_socket):
    global stop
    col = input("Enter a column: ")
    if col.lower() == "exit":
        print("You have abandonated the game")
        send_dc_me_message(client_socket)
    else:
        send_move(col, client_socket)

def send_move(column, client_socket):
    message = {'header':p.MOVE, 'column': column}
    p.send_one_message(client_socket, message)

def manage_valid_move(message):
    valid = message['valid']
    text = message['message']
    if not valid:
        print(text)


def manage_send_end_game(message):
    global stop

    win = message['win']
    if win:
        print('WINNER')
    else:
        print('LOSER')
    stop = True

def send_dc_me_message(client_socket):

    message = {'header': p.SEND_DC_ME}
    p.send_one_message(client_socket, message)

def manage_send_dc_server(message):
    global stop

    reason = message['reason']
    print(reason)
    stop = True

def manage_message(message, client_socket):
    global stop
    header = message['header']
    if header == p.MSG_WELCOME:
        stop = manage_msg_welcome(message, client_socket)
    elif header == p.SERVER_MESSAGE:
        manage_server_message(message)
    elif header == p.MSG_YOUR_TURN:
        manage_your_turn(client_socket)
    elif header == p.VALID_MOVE:
        manage_valid_move(message)
    elif header == p.MSG_SEND_GAMES:
        manage_msg_send_games(message, client_socket)
    elif header == p.SEND_VALID_GAME:
        manage_send_valid_game(message)
    elif header == p.SEND_END_GAME:
        manage_send_end_game(message)
    elif header == p.SEND_DC_SERVER:
        manage_send_dc_server(message)
    else:
        raise p.InvalidProtocol
def start(name, client_socket):
    global stop
    try:
        send_join(name, client_socket)
        while not stop:
            message = p.recv_one_message(client_socket)
            manage_message(message, client_socket)
        client_socket.close()
    except p.InvalidProtocol as e:
        print(e)
    except p.ConnectionClosed as e:
        print(e)

c_s = None
try:
    name, ip, port = client_parse_args()
    port_ok, name_ok = client_check_args(port, name)
    if port_ok and name_ok:
        c_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_s.connect((ip, int(port)))
        start(name, c_s)
except ConnectionResetError:
    print("Conection closed")
except ArgsError as e:
    print(e)

except getopt.GetoptError:
    print("Invalid arguments. ")

except KeyboardInterrupt:
    if c_s:
        send_dc_me_message(c_s)
    print("Bye.")
except (ConnectionRefusedError, TimeoutError):
    print("Could not connect to the server. ")
except BrokenPipeError:
    print("The server is disconnected")