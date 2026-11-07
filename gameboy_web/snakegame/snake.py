
from .utils import Direction, GameOverException

class Snake:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.body = [(5, 5), (4, 5), (3, 5)]
        self.grow = False

    def move(self, direction, food):
        x, y = self.body[0]
        dx, dy = direction.value
        new_head = (x + dx, y + dy)

        if new_head[0] < 0 or new_head[0] >= self.grid_width or new_head[1] < 0 or new_head[1] >= self.grid_height:
            raise GameOverException()

        if new_head in self.body[1:]:
            raise GameOverException()

        self.body.insert(0, new_head)

        if new_head == food.position:
            food.relocate(self.body)
            return True
        else:
            self.body.pop()
            return False
