import socket
import json
import protocols as p


def ask_command():
    exit = False
    commands = ["recibir", "plantarse", "salir"]
    while not exit:
            n = input("Choose: " + str(commands))
            if n.lower() in commands:
                exit = True
    return n


try:
    c_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_s.connect(("127.0.0.1", 20416))
    ask_menu = {"protocol": p.JOIN}
    p.send_one_message(c_s, json.dumps(ask_menu).encode())
    answer = json.loads(p.recv_one_message(c_s).decode())
    accepted = answer["accepted"]
    if accepted:
        exit = False
        while not exit:
            command = ask_command()
            d_number = {"protocol": p.SEND_COMMAND, "command": command}
            p.send_one_message(c_s, json.dumps(d_number).encode())
            if command.lower() == "salir":
                exit = True
                print("The has ido de la partida. ¡Adiós!")
            else:
                answer = json.loads(p.recv_one_message(c_s).decode())
                if answer["finish"]:
                    print(answer["answer"])
                    exit = True
                else:
                    print(answer["answer"])
    else:
        print(answer["reason"])

except KeyboardInterrupt:
    print("Bye.")
except ConnectionRefusedError:
    print("Could not connect to the server.")
except BrokenPipeError:
    print("El servidor ha sido desconectado")

