import asyncio
import os
import platform
import pygame
from .maze_generator import generate_maze
from .player import Player
from .point import Point
from .exit import Exit

TILE_SIZE = 32
ROWS, COLS = 20, 20
WIDTH, HEIGHT = TILE_SIZE * COLS, TILE_SIZE * ROWS
WHITE, BLACK, GREEN, RED, YELLOW = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (255, 255, 0)

GAME_TIME_MS = 90 * 1000      
SKIP_PENALTY_MS = 10 * 1000   

GAME_DIR = os.path.join("LabiryntGame", "Labiryntgame")
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
LABIRYNT_ID = 3
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


screen = None
font = small_font = score_font = None
player_img = gate_img = wall_img = None


def init():
    global screen, font, small_font, score_font, player_img, gate_img, wall_img
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Labirynt")

    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 24)
    score_font = pygame.font.Font(None, 36)

    def load(name):
        img = pygame.image.load(asset(name)).convert_alpha()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

    player_img = load("rycerz.png")
    gate_img = load("brama.png")
    wall_img = load("sciana.png")


def draw_maze(maze):
    for y, row in enumerate(maze):
        for x, tile in enumerate(row):
            if tile == 0:
                pygame.draw.rect(screen, WHITE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            else:
                screen.blit(wall_img, (x * TILE_SIZE, y * TILE_SIZE))


def draw_score(score):
    for i in range(3):
        color = YELLOW if i < score else (100, 100, 100)
        pygame.draw.circle(screen, color, (WIDTH - 100 + i * 25, 20), 10)


def new_level():
    reserved = [(1, 1), (18, 18)]
    maze = generate_maze(ROWS, COLS, reserved_positions=reserved)
    player = Player(1, 1)
    point = Point(maze)
    exit_tile = Exit(maze)
    return maze, player, point, exit_tile


def draw_hud(time_left_ms, levels):
    secs = max(0, time_left_ms) // 1000
    color = RED if secs <= 10 else BLACK
    timer_text = score_font.render(f"Czas: {secs // 60}:{secs % 60:02d}", True, color)
    levels_text = score_font.render(f"Poziomy: {levels}", True, BLACK)
    screen.blit(timer_text, (10, 5))
    screen.blit(levels_text, (10, 35))


async def game_loop():
    maze, player, point, exit_tile = new_level()

    clock = pygame.time.Clock()
    message = ""
    game_over = False
    result_message = ""
    levels_done = 0
    score_sent = False
    deadline = pygame.time.get_ticks() + GAME_TIME_MS

    while True:
        screen.fill(WHITE)

        time_left = deadline - pygame.time.get_ticks()

        
        if not game_over and time_left <= 0:
            game_over = True
            result_message = f"Koniec czasu! Ukończone poziomy: {levels_done}"
            if not score_sent:
                send_score(LABIRYNT_ID, levels_done)
                score_sent = True

        if not game_over:
            draw_maze(maze)
            screen.blit(player_img, (player.x * TILE_SIZE, player.y * TILE_SIZE))

            if player.score < 3:
                pygame.draw.circle(screen, YELLOW,
                                   (point.x * TILE_SIZE + TILE_SIZE // 2, point.y * TILE_SIZE + TILE_SIZE // 2),
                                   TILE_SIZE // 3)

            gate_x = exit_tile.x * TILE_SIZE
            gate_y = exit_tile.y * TILE_SIZE
            screen.blit(gate_img, (gate_x, gate_y))
            pygame.draw.rect(screen, GREEN, (gate_x, gate_y, TILE_SIZE, TILE_SIZE), 3)

            draw_score(player.score)
            draw_hud(time_left, levels_done)

            if message:
                screen.blit(small_font.render(message, True, (255, 0, 0)), (20, HEIGHT - 40))
        else:
            text1 = font.render(result_message, True, (0, 0, 0))
            text2 = font.render("Chcesz zagrać jeszcze raz? Naciśnij Enter.", True, (0, 0, 0))
            screen.blit(text1, text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            screen.blit(text2, text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not score_sent and levels_done > 0:
                    send_score(LABIRYNT_ID, levels_done)
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not score_sent and levels_done > 0:
                        send_score(LABIRYNT_ID, levels_done)
                    return False

                if not game_over:
                    
                    if event.key == pygame.K_n:
                        deadline -= SKIP_PENALTY_MS
                        maze, player, point, exit_tile = new_level()
                        message = ""
                        continue

                    
                    if player.move(event.key, maze):
                        player.x, player.y = 1, 1
                        message = "Ściana! Wracasz na start."
                    else:
                        message = ""

                    if player.x == point.x and player.y == point.y and player.score < 3:
                        player.score += 1
                        message = ""
                        if player.score < 3:
                            point.move_random(maze)

                    if player.x == exit_tile.x and player.y == exit_tile.y:
                        if player.score == 3:
                            
                            levels_done += 1
                            maze, player, point, exit_tile = new_level()
                            message = ""
                        else:
                            message = "Musisz zebrać 3 gwiazdki, aby wyjść!"
                else:
                    if event.key == pygame.K_RETURN:
                        return True

        pygame.display.flip()
        clock.tick(10)
        await asyncio.sleep(0)


async def main():
    init()
    while True:
        should_continue = await game_loop()
        if not should_continue:
            break