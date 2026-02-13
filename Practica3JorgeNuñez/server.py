import socket
import threading
import os
import protocols as p
import signal
from args import server_check_args, server_parse_args
from dashboard import Dashboard
import getopt
from linked_list import LinkedList


MIN_MENU_OPTION = 1
MAX_MENU_OPTION = 3

names = LinkedList()
games = LinkedList()
finish_games = 0

client_threads_running = []


def menu():
    message = ""
    message += "Please select an option" + "\n"
    message += "1.- Create game " + "\n"
    message += "2.- Join game " + "\n"
    message += "3.- Exit" + "\n"
    return message

def send_welcome(accepted, message, options_range, client_socket):
    message = {'header': p.MSG_WELCOME, 'accepted': accepted, 'message': message, 'options_range': options_range}
    p.send_one_message(client_socket, message)


def manage_msg_join(name, client_socket):
    global names
    if names.find(name):
        print(f"{name} is trying to connect: Rejected")
        send_welcome(False, "The name is used", None, client_socket)

    else:
        names.add_first(name)
        print(f"{name} is connected: Accepted")
        send_welcome(True, menu(), [1, 2, 3], client_socket)


def send_dc_server(reason, client_socket):
    message = {'header': p.SEND_DC_SERVER, 'reason': reason}
    p.send_one_message(client_socket, message)

def send_games(client_socket):
    global games

    if games.length() == 0:
        send_server_message_to_one("There are not actives games", client_socket)
        send_welcome(True, menu(), [1, 2, 3], client_socket)
    else:
        msg = "--------------\n"
        msg += "Available games \n"
        msg += "-------------\n"
        for index in range(games.length()):
            game = games.get(index)
            msg += f"In the game {index + 1} there is {game.number_of_players()}/2 players \n"
        msg += "------------\n"
        msg += "Choose one game to join: "
        message = {'header': p.MSG_SEND_GAMES, 'message': msg, 'Options_Range': [1, games.length()]}
        p.send_one_message(client_socket, message)

def send_server_message_to_one(text, client_socket):
    message = {'header': p.SERVER_MESSAGE, 'message': text}
    p.send_one_message(client_socket, message)

def manage_send_server_option(option, name, client_socket, client_address):
    global names, games

    stop = False
    if option == 1:
        game = Dashboard()
        game.add_player(name, client_socket, client_address)
        games.add_last(game)

        print(f"{name} create a  new game. Waiting for other player to join the game")
        send_server_message_to_one("Waiting for other player to join the game...", client_socket)
    elif option == 2:

        send_games(client_socket)
    else:
        names.delete(name)
        print(f"{name} disconnected")
        send_dc_server("Bye!", client_socket)
        stop = True
    return stop

def send_server_message_to_all(text, client_sockets):
    for client_socket in client_sockets:
        send_server_message_to_one(text, client_socket)

def send_your_turn(client_socket):
    message = {'header': p.MSG_YOUR_TURN}
    p.send_one_message(client_socket, message)

def send_end_game(winner, game):
    global games, names, finish_games
    if winner:
        print(f"{winner} has won the game! Game has finished")
    else:
        print(f"{game.players_names()} game has finished." "Dashboard is full. Nobody wins")

    for player in range(game.number_of_players()):
        if game.client_info['client_names'][player] == winner:
            message = { 'header': p.SEND_END_GAME, 'win': True}
        else:
            message = {'header': p.SEND_END_GAME, 'win': False}
        p.send_one_message(game.client_info['client_sockets'][player], message)
        names.delete(game.client_info['client_names'][player])
    games.delete(game.client_info['client_addresses'][0])
    finish_games += 1


def send_valid_game(joined, reason, client_socket):
    message = {'header': p.SEND_VALID_GAME, 'joined': joined, 'reason': reason}
    p.send_one_message(client_socket, message)


def manage_send_game_choice(message, name, client_socket, client_address):
    global games
    option = message['option'] - 1
    if 0 <= option < games.length():
        game = games.get(option)

        if game.is_full():
            joined = False
            print(f"{name} is trying to join a game. Rejected because the game is full ")
            reason1 = f"The game {option + 1} is full"
            send_valid_game(joined, reason1, client_socket)
            send_welcome(True, menu(), [1, 2, 3], client_socket)

        else:
            game.add_player(name, client_socket, client_address)
            creator_name = game.creator_name()
            creator_socket = game.creator_socket()

            print(f"The player {name} is joined")
            joined = True
            reason2 = "The game is started"
            print(reason2)
            send_valid_game(joined, reason2, client_socket)
            text1 = f" Waiting for {creator_name}"
            send_server_message_to_one(text1, client_socket)
            text2 = "--Game started--"
            send_server_message_to_one(text2, creator_socket)
            dash = str(Dashboard())
            send_server_message_to_one(dash, creator_socket)
            text3 = "This is your turn"
            send_server_message_to_one(text3, creator_socket)
            send_your_turn(creator_socket)

    else:
        joined = False
        reason3 = f"The game with id {option + 1} doesn't exist"
        send_valid_game(joined, reason3, client_socket)
        send_welcome(True, menu(), [1, 2, 3], client_socket)


def send_valid_move(valid, text, client_socket):
    message = {'header': p.VALID_MOVE, 'valid': valid, 'message': text}
    p.send_one_message(client_socket, message)


def manage_move(message, name, client_socket, client_address):
    global games
    stop = False
    col = message['column']
    try:
        stop = False
        col = int(col)
        if 1 <= col <= 10:
            game : Dashboard = games.get_node(client_address)
            if game:
                player = game.turn
                col = col - 1
                row = game.put_token(player + 1, col)
                print(f"{name}'s move: {col + 1} Valid")
                winner = game.check_winner(player + 1, col, row)
                opponent_socket = game.opponent_socket()
                opponent_name = game.opponent_name()
                full_dashboard = game.check_dashboard()
                g = str(game)
                if winner:
                    stop = True
                    message1 = f"The player: {name} is winner!"
                    send_server_message_to_one(message1, client_socket)
                    send_server_message_to_one(g, client_socket)
                    message1 = f"The player: {name} is winner!"
                    send_server_message_to_one(message1, opponent_socket)
                    send_server_message_to_one(g, opponent_socket)
                    send_end_game(name, game)
                elif full_dashboard:
                    stop = True
                    message3 = " The dashboard is full"
                    send_server_message_to_all(message3, game.client_info['client_sockets'])
                    send_server_message_to_all(g, game.client_info['client_sockets'])
                    send_end_game(name, game)
                else:
                    game.change_turn()
                    send_server_message_to_one(g, client_socket)
                    message5 = f"Waiting for {opponent_name}..."
                    send_server_message_to_one(message5, client_socket)
                    send_server_message_to_one(g, opponent_socket)
                    message6 = "This is your turn"
                    send_server_message_to_one(message6, opponent_socket)
                    send_your_turn(opponent_socket)
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
    global games, finish_games, names
    game = games.get_node(client_address)
    if game:
        print(f"{name} abandoned the game. Game has finished")
        reason = f"{name} abandoned the game. You have been disconnected."
        message = {'header': p.SEND_DC_SERVER, 'reason': reason}
        for player in range(game.number_of_players()):
            print(f"{game.client_info['client_names'][player]} was disconnected")
            if game.client_info['client_names'][player]!= name:
                p.send_one_message(game.client_info['client_sockets'][player], message)
            names.delete(game.client_info['client_names'][player])
        games.delete(client_address)
        finish_games += 1
    else:
        print(f"{name} is disconnected")
        names.delete(name)

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

class ServerThread(threading.Thread):
    IP = "127.0.0.1"

    @staticmethod
    def shutdown():
        global games
        reason = "The server has been shut down by the admin. You have been disconnected"
        msg = {'header': p.SEND_DC_SERVER, 'reason': reason}
        for i in range(games.length()):
            game = games.get(i)
            for player in range(game.number_of_players()):
                print(f"{game.client_info['client_names'][player]} was disconnected")
                p.send_one_message(game.client_info['client_sockets'][player], msg)
            print("The server has been closed by the admin")

    @staticmethod
    def n_games():
        global games, finish_games
        print(f"Active games: {games.length()}")
        print(f"Finished games: {finish_games}")
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ServerThread.IP, port))
        self.server_socket.listen()
        self.stop = False

    def run(self):
        global client_threads_running

        print(f"Listening on port {self.port}:")
        while not self.stop:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_handler = ClientThread(client_socket, client_address)
                client_handler.start()
                client_threads_running.append(client_handler)
            except OSError:
                self.stop = True
                print("Server closed")

pid = os.getpid()
server = None
try:
    port = server_parse_args()
    port_ok = server_check_args(port)
    if port_ok:
        port = int(port)

        server = ServerThread(port)
        server.start()
        stop = False
        while not stop:
            command = input()
            if command.lower() == "shutdown":
                stop = True
                ServerThread.shutdown()
            elif command.lower() == "ngames":
                ServerThread.n_games()
            else:
                "Invalid command"

    else:
        print("Please enter a correct port")
except getopt.GetoptError:
    print("Invalid arguments")

except KeyboardInterrupt:
    print("Server stopped by admin")

os.kill(pid, signal.SIGKILL)