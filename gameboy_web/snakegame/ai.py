from collections import deque
from .utils import Direction

GRID_W = 37   
GRID_H = 37

_STEPS = [
    (Direction.UP, (0, -1)),
    (Direction.DOWN, (0, 1)),
    (Direction.LEFT, (-1, 0)),
    (Direction.RIGHT, (1, 0)),
]


def build_model():
    return None


def train_model(model):
    pass


def predict_move(model, snake, food):
    body = [tuple(c) for c in snake.body]
    head = body[0]
    target = tuple(food.position)
    blocked = set(body[:-1])  

    def free(c):
        return 0 <= c[0] < GRID_W and 0 <= c[1] < GRID_H and c not in blocked

    queue = deque([(head, None)])
    seen = {head}
    while queue:
        pos, first = queue.popleft()
        if pos == target and first is not None:
            return first
        for d, (dx, dy) in _STEPS:
            nxt = (pos[0] + dx, pos[1] + dy)
            if nxt in seen or not free(nxt):
                continue
            seen.add(nxt)
            queue.append((nxt, first if first is not None else d))

    for d, (dx, dy) in _STEPS:  
        if free((head[0] + dx, head[1] + dy)):
            return d
    return Direction.UP

