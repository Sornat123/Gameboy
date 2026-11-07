import asyncio
import os
import platform
import pygame
from .snake import Snake
from .food import Food
from .utils import Direction, GameOverException

try:
    from .ai import build_model, train_model, predict_move
    AI_AVAILABLE = True
except Exception as e:
    print("AI niedostepne:", e)
    AI_AVAILABLE = False

GAME_DIR = "snakegame"
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = GAME_DIR


def asset(name):
    for base in (BASE_DIR, GAME_DIR):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return p
    return os.path.join(BASE_DIR, name)


# --- WYSYLANIE WYNIKOW DO BACKENDU ---
API_URL = "http://127.0.0.1:8001"
SNAKE_ID = 1
_token = None


def get_token():
    global _token
    if _token:
        return _token
    try:
        h = str(platform.window.location.hash)
        if "token=" in h:
            _token = h.split("token=")[1].split("&")[0]
    except Exception:
        pass
    return _token


def send_score(game_id, score):
    token = get_token()
    if not token:
        print("Gosc - wynik nie zapisany")
        return
    js = f"""
    fetch('{API_URL}/api/scores', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'
        }},
        body: JSON.stringify({{game_id: {int(game_id)}, score: {int(score)}}})
    }}).then(r => console.log('SCORE STATUS', r.status))
      .catch(e => console.log('SCORE ERROR', e));
    """
    try:
        platform.window.eval(js)
    except Exception as e:
        print("Blad wysylania wyniku:", e)


WIDTH, HEIGHT = 750, 750
CELL_SIZE = 20
HEAD_SCALE = 1.8
APPLE_SCALE = 1.2

GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 10

head_size = int(CELL_SIZE * HEAD_SCALE)
apple_size = int(CELL_SIZE * APPLE_SCALE)

screen = None
font = small_font = None
background_img = snake_img = apple_img = None


def init():
    global screen, font, small_font, background_img, snake_img, apple_img
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game z AI")
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)

    background_img = pygame.image.load(asset("tlo.png"))
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    snake_img = pygame.transform.scale(
        pygame.image.load(asset("waz.png")), (head_size, head_size))
    apple_img = pygame.transform.scale(
        pygame.image.load(asset("apple.png")), (apple_size, apple_size))


def draw_text(text, fnt, color, x, y):
    textobj = fnt.render(text, True, color)
    screen.blit(textobj, textobj.get_rect(center=(x, y)))


async def mode_menu():
    screen.blit(background_img, (0, 0))
    draw_text("Snake Game", font, (0, 255, 0), WIDTH // 2, HEIGHT // 2 - 50)
    draw_text("Nacisnij H by grac jako gracz", small_font, (255, 255, 255), WIDTH // 2, HEIGHT // 2)
    if AI_AVAILABLE:
        draw_text("Nacisnij A by gralo AI", small_font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 40)
    draw_text("ESC - powrot do menu", small_font, (200, 200, 200), WIDTH // 2, HEIGHT // 2 + 100)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_h:
                    return False
                if event.key == pygame.K_a and AI_AVAILABLE:
                    return True
        await asyncio.sleep(0)


async def play(use_ai):
    """Jedna rozgrywka. Zwraca 'restart' albo None (powrot do menu)."""
    clock = pygame.time.Clock()
    snake = Snake(GRID_WIDTH, GRID_HEIGHT)
    food = Food(GRID_WIDTH, GRID_HEIGHT, snake.body)
    model = None
    if use_ai:
        model = build_model()
        train_model(model)

    score = 0
    direction = Direction.RIGHT

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if not use_ai:
                    if event.key == pygame.K_UP and direction != Direction.DOWN:
                        direction = Direction.UP
                    elif event.key == pygame.K_DOWN and direction != Direction.UP:
                        direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and direction != Direction.RIGHT:
                        direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and direction != Direction.LEFT:
                        direction = Direction.RIGHT

        try:
            if use_ai:
                direction = predict_move(model, snake, food)
            if snake.move(direction, food):
                score += 1
        except GameOverException:
            
            if not use_ai:
                send_score(SNAKE_ID, score)

            draw_text("Game Over", font, (255, 0, 0), WIDTH // 2, HEIGHT // 2 - 50)
            draw_text("Nacisnij R by zrestartowac", small_font, (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 10)
            pygame.display.flip()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            return "restart"
                        if event.key == pygame.K_ESCAPE:
                            return None
                await asyncio.sleep(0)

        screen.blit(background_img, (0, 0))

        for i, (x, y) in enumerate(snake.body):
            if i == 0:
                off = (CELL_SIZE - head_size) // 2
                screen.blit(snake_img, (x * CELL_SIZE + off, y * CELL_SIZE + off))
            else:
                pygame.draw.rect(screen, (0, 255, 0), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        fx, fy = food.position
        off = (CELL_SIZE - apple_size) // 2
        screen.blit(apple_img, (fx * CELL_SIZE + off, fy * CELL_SIZE + off))

        draw_text(f"Wynik: {score}", small_font, (255, 255, 255), 60, 20)
        pygame.display.flip()

        await asyncio.sleep(0)


async def main():
    init()
    use_ai = await mode_menu()
    if use_ai is None:
        return
    while True:
        result = await play(use_ai)
        if result != "restart":
            return