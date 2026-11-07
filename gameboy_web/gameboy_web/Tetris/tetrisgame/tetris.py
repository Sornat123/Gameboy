import pygame
import random
from .piece import Piece
from .config import *

class Tetris:
    def __init__(self):
        self.board = [[(0, 0, 0) for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.fall_counter = 0

    def get_new_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        color = random.choice(COLORS)
        return Piece(shape, color)

    def valid_position(self, piece, dx=0, dy=0, rotation=None):
        shape = piece.image(rotation)
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.board[new_y][new_x] != (0, 0, 0):
                        return False
        return True

    def lock_piece(self):
        shape = self.current_piece.image()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current_piece.x + x
                    py = self.current_piece.y + y
                    if py < 0:
                        self.game_over = True
                        return
                    self.board[py][px] = self.current_piece.color
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        if not self.valid_position(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.board) if (0, 0, 0) not in row]
        for i in lines_to_clear:
            del self.board[i]
            self.board.insert(0, [(0, 0, 0) for _ in range(COLS)])
            self.score += 100

    def rotate(self):
        if self.valid_position(self.current_piece, rotation=(self.current_piece.rotation + 1) % len(self.current_piece.shape)):
            self.current_piece.rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)

    def move(self, dx):
        if self.valid_position(self.current_piece, dx=dx):
            self.current_piece.x += dx

    def soft_drop(self):
        if self.valid_position(self.current_piece, dy=1):
            self.current_piece.y += 1
        else:
            self.lock_piece()

    def update(self):
        self.fall_counter += 1
        if self.fall_counter >= DROP_SPEED:
            self.soft_drop()
            self.fall_counter = 0

    def draw(self, win):
        
        for y in range(ROWS):
            for x in range(COLS):
                pygame.draw.rect(win, self.board[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        
        shape = self.current_piece.image()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.current_piece.x + x
                    py = self.current_piece.y + y
                    if py >= 0:
                        pygame.draw.rect(win, self.current_piece.color, (px * BLOCK_SIZE, py * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        
        for x in range(COLS):
            pygame.draw.line(win, (40, 40, 40), (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
        for y in range(ROWS):
            pygame.draw.line(win, (40, 40, 40), (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

        
        pygame.draw.rect(win, (255, 255, 255), (0, 0, COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE), 2)
