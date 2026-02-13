import socket
import threading
import os
import protocols as p
import signal
from args import server_check_args, server_parse_args
from dashboard import Dashboard
import getopt

MIN_MENU_OPTION = 1
MAX_MENU_OPTION = 3

id = 1
games = {}
client_game = {}
client_threads_running = []


def menu():
    message = ""
    message += "Please select an option" + "\n"
    message += "1.- Create game " + "\n"
    message += "2.- Join game " + "\n"
    message += "3.- Exit" + "\n"
    return message

def send_welcome(client_socket):
    message = {'header': p.MSG_WELCOME, 'accepted': True, 'message': menu(), 'options_range': [1, 2, 3]}
    p.send_one_message(client_socket, message)


def manage_msg_join(name, client_socket):
    print(f"{name} is connected")
    send_welcome(client_socket)
    return name

def send_dc_server(reason, client_socket):
    message = {'header': p.SEND_DC_SERVER, 'reason': reason}
    p.send_one_message(client_socket, message)

def send_games(client_socket):
    ids = []
    menu = "--------------\n"
    menu += "Available games \n"
    menu += "-------------\n"
    for id, game in games.items():
        menu += f"In the game {id} there is {len(game['players'])}/2 players \n"
        ids.append(id)
    menu += "------------\n"
    menu += "Choose one game to join: "
    message = {'header': p.MSG_SEND_GAMES, 'message': menu, 'Options_Range': ids}
    p.send_one_message(client_socket, message)

def send_server_message_to_one(text, client_socket):
    message = {'header': p.SERVER_MESSAGE, 'message': text}
    p.send_one_message(client_socket, message)

def manage_send_server_option(option, name, client_socket, client_address):
    stop = False
    if option == 1:
        global id, games, client_game
        game = {'id': id, 'dashboard': Dashboard(), 'players': [{'name': name, 'client_socket': client_socket, 'client_address': client_address}], 'turn': 0}
        games[id] = game
        client_game[client_address] = id
        id += 1
        print(f"{name} create a  new game. Waiting for other player to join the game")
        send_server_message_to_one("Waiting for other player to join the game...", client_socket)
    elif option == 2:

        send_games(client_socket)
    else:
        print(f"{name} disconnected")
        send_dc_server("Bye!", client_socket)
        stop = True
    return stop

def send_server_message_to_all(text, players):
    for player in players:
        send_server_message_to_one(text, player['client_socket'])

def send_your_turn(client_socket):
    message = {'header': p.MSG_YOUR_TURN}
    p.send_one_message(client_socket, message)

def send_end_game(winner, game):
    global games, client_game
    for player in game['players']:
        if player['name'] == winner:
            message = { 'header': p.SEND_END_GAME, 'win': True}
        else:
            message = {'header': p.SEND_END_GAME, 'win': False}
        p.send_one_message(player['client_socket'], message)
        if client_game[player['client_address']]:
            del client_game[player['client_address']]
    if games[game['id']]:
        del games[game['id']]

def game_is_full(game):
    full = False
    if len(game['players']) == 2:
        full = True
    return full

def game_creator_player(game):
    creator = game['players'][0]
    return creator

def send_valid_game(joined, reason, client_socket):
    message = {'header': p.SEND_VALID_GAME, 'joined': joined, 'reason': reason}
    p.send_one_message(client_socket, message)

def manage_send_game_choice(message, name, client_socket, client_address):
    global games
    option = message['option']
    client_game[client_address] = option
    if option in games:
        game = games[option]
        if game_is_full(game):
            joined = False
            print("This game is full, please choose other game")
            reason1 = f"The game {option} is full"
            send_valid_game(joined, reason1, client_socket)
            send_welcome(client_socket)
        else:
            player = {'name': name, 'client_socket': client_socket, 'client_address':client_address}
            creator = game_creator_player(game)

            game['players'].append(player)
            print(f"The player {player['name']} is joined")
            joined = True
            reason2 = "The game is started"
            print(reason2)
            send_valid_game(joined, reason2, client_socket)
            text1 = f" Waiting for {creator['name']}"
            send_server_message_to_one(text1, client_socket)
            text2 = "--Game started--"
            send_server_message_to_one(text2, creator['client_socket'])
            dash = str(Dashboard())
            send_server_message_to_one(dash, creator['client_socket'])
            text3 = "This is your turn"
            send_server_message_to_one(text3, creator['client_socket'])
            send_your_turn(creator['client_socket'])

    else:
        joined = False
        reason3 = f"The game with id {option} doesn't exist"
        send_valid_game(joined, reason3, client_socket)
        send_welcome(client_socket)

def game_by_client_address(client_address):
    global client_game, games
    if client_address in client_game:
        game_id = client_game[client_address]
        return games[game_id]
    return None


def player_index(game, name):
    if game.turn == 0:
        position = 0
    else:
        position = 1
    return position


def opponent_player(game):
    turn = game['turn']
    opponent = game['players'][(turn + 1) % 2]
    return opponent


def send_valid_move(valid, text, client_socket):
    message = {'header': p.VALID_MOVE, 'valid': valid, 'message': text}
    p.send_one_message(client_socket, message)


def manage_move(message, name, client_socket, client_address): # name o game?
    stop = False
    col = message['column']
    try:
        stop = False
        col = int(col)
        if 1 <= col <= 10:
            game = game_by_client_address(client_address)
            if game:
                dash = game['dashboard']
                player = (game['turn'] + 1) % 2
                col = col - 1
                row = dash.put_token(player + 1, col)
                print(f"{name}'s move: {col + 1} Valid")
                winner = dash.check_winner(player + 1, col, row)
                opponent = opponent_player(game)
                full_dashboard = dash.check_dashboard()
                if winner:
                    stop = True
                    message1 = f"The player: {name} is winner!"
                    send_server_message_to_one(message1, client_socket)
                    send_server_message_to_one(str(dash), client_socket)
                    message1 = f"The player: {name} is winner!"
                    send_server_message_to_one(message1, opponent['client_socket'])
                    send_server_message_to_one(str(dash), opponent['client_socket'])
                    send_end_game(name, game)
                elif full_dashboard:
                    stop = True
                    message3 = " The dashboard is full"
                    send_server_message_to_one(message3, client_socket)
                    send_server_message_to_one(message3, opponent['client_socket'])
                    send_server_message_to_one(str(dash), client_socket)
                    send_server_message_to_one(str(dash), opponent['client_socket'])
                    send_end_game(name, game)
                else:
                    game['turn'] = (game['turn'] + 1) % 2
                    send_server_message_to_one(str(dash), client_socket)
                    message5 = f"Waiting for {opponent['name']}..."
                    send_server_message_to_one(message5, client_socket)
                    send_server_message_to_one(str(dash), opponent['client_socket'])
                    message6 = "This is your turn"
                    send_server_message_to_one(message6, opponent['client_socket'])
                    send_your_turn(opponent['client_socket'])
            else:
                send_dc_server("The game you were playing is no longer exists", client_socket)
        else:
            raise ValueError
    except Dashboard.ColumnFull:
        text = "The column is full"
        print(text)
        valid = False
        send_valid_move(valid, text, client_socket)
        send_server_message_to_one("This is your turn", client_socket)
        send_your_turn(client_socket)
    except ValueError:
        print("The column is invalid")
        valid = False
        send_valid_move(valid, "The column is invalid", client_socket)
        send_server_message_to_one("This is your turn", client_socket)
        send_your_turn(client_socket)
    return stop


def manage_dc_me(name, client_address):
    global games, client_game
    game = game_by_client_address(client_address)
    if game:
        print(f"{name} abandoned the game. Game has finished")
        reason = f"{name} abandoned the game. You have been disconnected."
        message = {'header': p.SEND_DC_SERVER, 'reason': reason}
        for player in game['players']:
            print(f"{player['name']} was disconnected")
            if player['name'] != name:
                p.send_one_message(player['client_socket'], message)
            del client_game[player['client_address']]
        del games[game['id']]
    else:
        print(f"{name} is disconnected")

class ClientThread(threading.Thread):

    def __init__(self, c_s, c_a):
        threading.Thread.__init__(self)
        self.c_s = c_s
        self.c_a = c_a
        self.stop = False
        self.name = ""

    def manage_message(self, message):
        header = message['header']
        if header == p.MSG_JOIN:
            self.name = message['name']
            manage_msg_join(self.name, self.c_s)
        elif header == p.MSG_SEND_SERVER_OPTION:
            self.stop = manage_send_server_option(message['option'], self.name, self.c_s, self.c_a)
        elif header == p.MOVE:
            manage_move(message, self.name, self.c_s, self.c_a)
        elif header == p.SEND_GAMES_CHOICE:
            manage_send_game_choice(message, self.name, self.c_s, self.c_a)
        elif header == p.SEND_DC_ME:
            manage_dc_me(self.name, self.c_a)
            self.stop = True
        else:
            print("Invalid message received")

    def run(self):
        global client_threads_running
        while not self.stop:
            try:
                message = p.recv_one_message(self.c_s)
                self.manage_message(message)
            except OSError:
                self.stop = True
            except p.ConnectionClosed:
                self.stop = True

        print(f"ClientHandler [{self.name}] is closing...")
        client_threads_running.remove(self)

IP = "127.0.0.1"
pid = os.getpid()
try:
    port = server_parse_args()
    port_ok = server_check_args(port)
    if port_ok:
        port = int(port)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((IP, port))
        server_socket.listen()
        print(f"Listening on port {port}:")
        stop = False
        while not stop:
            try:
                client_socket, client_address = server_socket.accept()
                client_handler = ClientThread(client_socket, client_address)
                client_handler.start()
                client_threads_running.append(client_handler)
            except OSError:
                stop = True
                print("Server closed")
    else:
        print("Please enter a correct port")
except getopt.GetoptError:
    print("Invalid arguments")

except KeyboardInterrupt:
    print("Server stopped by admin")

os.kill(pid, signal.SIGKILL)