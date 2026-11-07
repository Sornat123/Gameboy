import pygame
import random

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def draw(self, screen, size):
        pygame.draw.circle(screen, (255, 255, 0), (self.x*size + size//2, self.y*size + size//2), size//4)

    def move_random(self, maze):
        empty = [(x, y) for y in range(len(maze)) for x in range(len(maze[0])) if maze[y][x] == 0]
        self.x, self.y = random.choice(empty)

class Exit:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def draw(self, screen, size):
        pygame.draw.rect(screen, (255, 0, 0), (self.x*size, self.y*size, size, size))