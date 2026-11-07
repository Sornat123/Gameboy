import pygame

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.score = 0

    def move(self, key, maze):
        dx, dy = 0, 0
        if key == pygame.K_LEFT:
            dx = -1
        elif key == pygame.K_RIGHT:
            dx = 1
        elif key == pygame.K_UP:
            dy = -1
        elif key == pygame.K_DOWN:
            dy = 1

        try:
            target_tile = maze[self.y + dy][self.x + dx]
            if target_tile == 0:
                self.x += dx
                self.y += dy
                return False  
            else:
                return True  
        except IndexError:
            print("Wyjście poza planszę!")
            return True  

    