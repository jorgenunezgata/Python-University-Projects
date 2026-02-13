import getopt, sys


def client_parse_args():
    ip = "127.0.0.1"
    name = ""
    port = 6123
    opts, args = getopt.getopt(sys.argv[1:], "n:i:p:", ["name=", "ip=", "port="])
    for o, a in opts:
        if o in ("-n", "--name"):
            name = a
        elif o in ("-i", "--ip"):
            ip = a
        elif o in ("-p", "--port"):
            port = a
    return name, ip, port


def client_check_args(port, name):
    port_ok = True
    name_ok = True
    try:
        n_port = int(port)
    except ValueError:
        port_ok = False

    if len(name) == 0:
        name_ok = False
    return port_ok, name_ok

def client_manage_errors( port_ok, name_ok):
    if not port_ok:
        print("Number of port [-p, --port] should be an integer number")
    if not name_ok:
        print(">YOu need yo enter a name using the [-n, --name] argument.")
def server_parse_args():
    port = 6123
    opts, args = getopt.getopt(sys.argv[1:], "p:", ["port"])
    for o, a in opts:
        if o in ("-p", "--port"):
            port = a
    return port

def server_check_args(port):
    port_ok = True
    try:
        n_port = int(port)
    except ValueError:
        port_ok = False
    return port_ok

