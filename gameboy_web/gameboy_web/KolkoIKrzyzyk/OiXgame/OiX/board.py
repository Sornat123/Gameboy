from .exceptions import InvalidMoveError

class Board:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]

    def make_move(self, row, col, player):
        if self.board[row][col] != ' ':
            raise InvalidMoveError("Pole zajęte")
        self.board[row][col] = player

    def check_winner(self):
        b = self.board
        lines = b + list(zip(*b)) + [
            [b[i][i] for i in range(3)],
            [b[i][2 - i] for i in range(3)]
        ]
        for line in lines:
            if line[0] != ' ' and all(x == line[0] for x in line):
                return line[0]
        if all(cell != ' ' for row in b for cell in row):
            return 'Remis'
        return None

    def reset(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]

    def empty_cells(self):
        return [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ' ']