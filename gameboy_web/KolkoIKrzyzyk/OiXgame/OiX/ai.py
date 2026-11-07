import random

LINES = [
    [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)],
]


def _winner(grid):
    for line in LINES:
        a, b, c = (grid[r][col] for r, col in line)
        if a != ' ' and a == b == c:
            return a
    return None


def _free(grid):
    return [
        (r, c)
        for r in range(3)
        for c in range(3)
        if grid[r][c] == ' '
    ]


def _minimax(grid, player, depth):
    w = _winner(grid)

    if w == 'O':
        return 10 - depth

    if w == 'X':
        return depth - 10

    moves = _free(grid)

    if not moves:
        return 0

    if player == 'O':
        best = -100

        for r, c in moves:
            grid[r][c] = 'O'
            best = max(best, _minimax(grid, 'X', depth + 1))
            grid[r][c] = ' '

    else:
        best = 100

        for r, c in moves:
            grid[r][c] = 'X'
            best = min(best, _minimax(grid, 'O', depth + 1))
            grid[r][c] = ' '

    return best


def get_ai_move(board):
    """Zwraca ruch bota jako (row, col)."""

    grid = [row[:] for row in board.board]
    moves = _free(grid)

    if not moves:
        return None

    
    for r, c in moves:
        grid[r][c] = 'O'

        if _winner(grid) == 'O':
            grid[r][c] = ' '
            return r, c

        grid[r][c] = ' '

    
    if random.random() < 0.25:
        return random.choice(moves)

    
    best_score = -100
    best_moves = []

    for r, c in moves:
        grid[r][c] = 'O'
        score = _minimax(grid, 'X', 1)
        grid[r][c] = ' '

        if score > best_score:
            best_score = score
            best_moves = [(r, c)]

        elif score == best_score:
            best_moves.append((r, c))

    return random.choice(best_moves)