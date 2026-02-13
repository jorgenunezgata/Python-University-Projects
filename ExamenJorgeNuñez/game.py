class Game:
    def __init__(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        self.total = 0
        self.computer_total = 0

    def __str__(self):
        return f"({self.client_socket.getpeername()[0]}, {self.client_socket.getpeername()[1]}): {self.total}"

    def __eq__(self, other):
        return self.client_socket == other