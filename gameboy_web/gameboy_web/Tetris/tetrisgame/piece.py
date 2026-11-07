import random
from .config import SHAPES, COLS

class Piece:
    def __init__(self, shape, color):
        self.shape = SHAPES[shape]
        self.color = color
        self.x = COLS // 2 - len(self.shape[0][0]) // 2
        self.y = -2  
        self.rotation = 0

    def image(self, rotation=None):
        if rotation is None:
            rotation = self.rotation
        return self.shape[rotation % len(self.shape)]