import random
from collections import deque


def _walls(rows, cols):
    return [[1] * cols for _ in range(rows)]


def generate_empty_maze(rows, cols):
    maze = _walls(rows, cols)
    for y in range(1, rows - 1):
        for x in range(1, cols - 1):
            maze[y][x] = 0
    return maze


def is_path(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    visited = [[False] * cols for _ in range(rows)]
    queue = deque([start])
    visited[start[1]][start[0]] = True

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return True
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx] and maze[ny][nx] == 0:
                visited[ny][nx] = True
                queue.append((nx, ny))
    return False


def generate_maze(rows, cols, reserved_positions=None):
    if reserved_positions is None:
        reserved_positions = []

    while True:
        maze = _walls(rows, cols)
        for y in range(1, rows - 1):
            for x in range(1, cols - 1):
                if (x, y) not in reserved_positions:
                    maze[y][x] = 0 if random.random() > 0.3 else 1
        for x, y in reserved_positions:
            maze[y][x] = 0
        if is_path(maze, (1, 1), (18, 18)):
            return maze

