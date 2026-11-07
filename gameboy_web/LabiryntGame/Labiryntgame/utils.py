class GameException(Exception):
    pass

def safe_move(x, y, maze):
    try:
        return maze[y][x] == 0
    except IndexError:
        raise GameException("Pozycja poza planszą!")