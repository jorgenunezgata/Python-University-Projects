class Cell:

    def __init__(self):
        self.player = None
        self.symbol = "-"

    def change_symbol(self, player):
        self.player = player
        if self.player == 1:
            self.symbol = "0"
        else:
            self.symbol = "X"

    def __str__(self):
        return self.symbol


class Dashboard:
    N_players = 2

    class ColumnFull(Exception):
        def __init__(self, column):
            super().__init__("Column " + str(column + 1) + " is full")

    def __init__(self):
        self.rows = 10
        self.dashboard = [[Cell() for col in range(0, 10)] for col in range(0, 10)]
        self.turn = 0

    def __str__(self):
        dash = ""
        for row in self.dashboard:
            for col in row:
                dash += str(col)
                dash += " "
            dash += "\n"
        return dash

    def get_user_column(row, player):
        col = None
        exit = False
        player = 0
        while not exit:
            col = input(f"Player {player + 1} insert a column: ")
            if col.lower() == "exit":
                exit = True
                col = None
            else:
                try:
                    col = int(col)
                    if 1 <= col <= row:
                        exit = True
                    else:
                        print(f"Please insert a valid column between {1} and {row} or 'exit' word")
                except ValueError:
                    print(f"Please insert a valid column between {1} and {row} or 'exit' word")
        return col


    def put_token(self, player, column):
        i = self.rows - 1
        exit = False
        while i >= 0 and not exit:
            if not self.dashboard[i][column].player:
                self.dashboard[i][column].change_symbol(player)
                exit = True
            else:
                i -= 1
        if i < 0:
            raise Dashboard.ColumnFull(column)
        return i

    def check_horizontal(self, player, col, row):
        col_start = col
        count_tokens = 0
        while col_start < self.rows and count_tokens < 4 and self.dashboard[row][col_start].player == player:
            count_tokens += 1
            col_start += 1
        col_start = col - 1
        while col_start >= 0 and count_tokens < 4 and self.dashboard[row][col_start].player == player:
            count_tokens += 1
            col_start -= 1
        return count_tokens == 4

    def check_vertical(self, player, col, row):
        row_start = row
        count_tokens = 0
        while row_start < self.rows and count_tokens < 4 and self.dashboard[row_start][col].player == player:
            count_tokens += 1
            row_start += 1
        return count_tokens == 4

    def check_first_diagonal(self, player, col, row):
        row_start = row
        col_start = col
        count_tokens = 0
        while row_start < self.rows and col_start < self.rows and count_tokens < 4 and self.dashboard[row_start][
            col_start].player == player:
            count_tokens += 1
            row_start += 1
            col_start += 1
        row_start = row - 1
        col_start = col - 1
        while row_start >= 0 and col_start >= 0 and count_tokens < 4 and self.dashboard[row_start][
            col_start].player == player:
            count_tokens += 1
            row_start -= 1
            col_start -= 1
        return count_tokens == 4

    def check_second_diagonal(self, player, col, row):
        row_start = row
        col_start = col
        count_tokens = 0
        while row_start < self.rows and col_start >= 0 and count_tokens < 4 and self.dashboard[row_start][
            col_start].player == player:
            count_tokens += 1
            row_start += 1
            col_start -= 1
        col_start = col + 1
        row_start = row - 1
        while row_start >= 0 and col_start < self.rows and count_tokens < 4 and self.dashboard[row_start][
            col_start].player == player:
            count_tokens += 1
            row_start -= 1
            col_start += 1
        return count_tokens == 4

    def check_diagonal(self, player, col, row):
        return self.check_first_diagonal(player, col, row) or self.check_second_diagonal(player, col, row)

    def check_winner(self, player, col, row):
        return self.check_horizontal(player, col, row) or self.check_vertical(player, col, row) or self.check_diagonal(
            player, col, row)

    def check_dashboard(self):
        full = True
        col = 0
        row = 0
        while full and col < self.rows:
            if self.dashboard[row][col].player is None:
                full = False
            col += 1
        return full
