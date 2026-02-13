import json
import os
import signal
import socket
import threading
import protocols as p
import random
from game import Game
from linkedlist import LinkedList



finishedgames = LinkedList()
games = LinkedList()
NUMBER_TO_WIN = 7.5
count = 0

def generate_number():
    n = random.randint(1, 10)
    if n > 7:
        n = 0.5
    return n

def generate_computer_numbers():
    global count
    computer_count = 0
    while computer_count < NUMBER_TO_WIN:
        computer_count += generate_number()
    return computer_count


class ClientThread(threading.Thread):
    def __init__(self, c_s, c_a):
        threading.Thread.__init__(self)
        self.c_s = c_s
        self.c_a = c_a
        self.end = False
    
    def send_accepted_message(self, accepted, reason):
         d_dc = {"protocol": p.DC, "accepted": accepted, "reason": reason}
         p.send_one_message(self.c_s, json.dumps(d_dc).encode())
    
    def send_answer(self, finish, answer):
        d_answer = {"finish": finish, "answer": answer}
        p.send_one_message(self.c_s, json.dumps(d_answer).encode())


    def manage_command(self, command, c_s):
        global games

        g : Game = games.get_node(c_s)
        if command == "recibir":
            g.total += generate_number()
            self.manage_number(g)
        elif command == "plantarse":
            g.computer_total = generate_computer_numbers()
            self.manage_computer_number(g)
        elif command == "salir":
            games.delete(g)
            finishedgames.add_last(g)

        else:
            g.total = 0
            self.end = True


    def manage_computer_number(self, g):
        global games, finishedgames
        if g.computer_total == NUMBER_TO_WIN:
            self.send_answer(True,  "You lost!. Your count is " + str(g.total) + \
                             " and the computer count is " + str(g.computer_total))
            games.delete(g)
            finishedgames.add_first(g)
        else:
            self.send_answer(True, "You won!. Your count is " + str(g.total) + \
                             " and the computer count is " + str(g.computer_total))
            games.delete(g)
            finishedgames.add_first(g)
        self.end = True

    def manage_number(self, g):
        global games, finishedgames
        if g.total == NUMBER_TO_WIN:
            self.send_answer(True,  "You won!")
            self.end = True
            games.delete(g)
            finishedgames.add_first(g)
        elif g.total < NUMBER_TO_WIN:
            self.send_answer(False,  "The total count is " + str(g.total))
        else:
            self.send_answer(True,  "You lost. Your total count is " + str(g.total))
            self.end = True
            g.total = 0
            finishedgames.add_first(g)
            games.delete(g)
		
    def run(self):
        try:
            while not self.end:
                message = json.loads(p.recv_one_message(self.c_s).decode())
                if message["protocol"] == p.SEND_COMMAND:
                    self.manage_command(message["command"], self.c_s)
                elif message['protocol'] == p.JOIN:
                    g = Game(self.c_s, self.c_a)
                    games.add_last(g)
                    self.send_accepted_message(True, "")
        except TypeError:
            print("Cliente desconectado")


class ServerThread(threading.Thread):

    @staticmethod
    def currentgames():
        global games
        if games.length() == 0:
            print("No existe ninguna partida que se este jugando ahora mismo")
        else:
            print(f"Ahora mismo existen un total de {games.length()} juegos y a continuación se mostrará la información de cada una de ellas:")
            for i in range(games.length()):
                game = games.get(i)
                if game.computer_total == 0:
                    print(f"El jugador del juego {i + 1} tiene una cuenta de {game.total}")
                else:
                    print(f"El jugador del juego {i +1} tiene una cuenta de {game.total} y la cuenta del ordeandor es {game.computer_total}")

    @staticmethod
    def finishedgames():
        global finishedgames
        if finishedgames == 0:
            print("No hay ninugna partida terminada")
        else:
            print(f"Finished games: {finishedgames.length()}")
            for i in range(finishedgames.length()):
                game = finishedgames.get(i)
                if game.computer_total == 0:
                    print(f"El jugador del juego {i + 1} ha tenido una cuenta de {game.total}")
                else:
                    print(f"El jugador del juego {i +1} ha tenido una cuenta de {game.total} y la cuenta del ordeandor era {game.computer_total}")


    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
        self.s_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s_s.bind(("0.0.0.0", 20416))
        self.s_s.listen(20)

    def run(self):
        while not self.end:
            print("Waiting connection...")
            c_s, c_a = self.s_s.accept()
            client_thread = ClientThread(c_s, c_a)
            client_thread.start()

pid = os.getpid()
server_thread = ServerThread()
try:
    server_thread.start()
    while not server_thread.end:
        command = input()
        if command.lower() == "currentgames":
            ServerThread.currentgames()
        elif command.lower() == "finishedgames":
            ServerThread.finishedgames()
        elif command.lower() == "exit":
            print("The server is closed by admin")
            ServerThread.end = True
            os.kill(pid, signal.SIGKILL)
        else:
            print("Invalid command")
    server_thread.end = True
    os.kill(pid, signal.SIGKILL)
except OSError:
    print("Address already in use.")
except KeyboardInterrupt:
    server_thread.end = True
    os.kill(pid, signal.SIGKILL)

