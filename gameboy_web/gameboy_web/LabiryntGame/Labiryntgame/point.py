import random

class Point:
    def __init__(self, maze):
        self.x, self.y = self.get_random_position(maze)

    def get_random_position(self, maze):
        while True:
            x = random.randint(0, len(maze[0]) - 1)
            y = random.randint(0, len(maze) - 1)
            if maze[y][x] == 0:
                return x, y

    def move_random(self, maze):
        self.x, self.y = self.get_random_position(maze)