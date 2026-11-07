import asyncio
import importlib
import os
import sys
import pygame

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

WIDTH, HEIGHT = 640, 640
TITLE = "Wirtualny Gameboy - Menu Główne"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

button_color = (30, 20, 70)
hover_color = (255, 0, 128)
text_color = (255, 255, 255)

games = [
    {"name": "Kółko i Krzyżyk", "module": "KolkoIKrzyzyk.OiXgame.OiX.main"},
    {"name": "Labirynt",        "module": "LabiryntGame.Labiryntgame.main"},
    {"name": "Snake",           "module": "snakegame.main"},
    {"name": "Tetris",          "module": "Tetris.tetrisgame.main"},
]

selected = 0
error_message = None
background = None
font = None


def load_assets():
    global background, font
    try:
        background = pygame.image.load(os.path.join(BASE_DIR, "tlo.png")).convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except Exception as e:
        print("Brak tla:", e)
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((26, 16, 43))

    try:
        font = pygame.font.Font(os.path.join(BASE_DIR, "assets", "pixel.ttf"), 24)
    except Exception as e:
        print("Brak czcionki:", e)
        font = pygame.font.Font(None, 32)


def restore_menu():
    global screen
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    load_assets()
    pygame.event.clear()


def draw_text_with_outline(text, x, y, color, outline_color):
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        screen.blit(font.render(text, True, outline_color), (x + dx, y + dy))
    screen.blit(font.render(text, True, color), (x, y))


def draw_menu():
    screen.blit(background, (0, 0))

    if error_message:
        err = font.render(error_message[:45], True, (255, 0, 0))
        screen.blit(err, (20, 20))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    for i, game in enumerate(games):
        x, y, w, h = 160, 320 + i * 60, 320, 50
        hovered = x <= mouse_x <= x + w and y <= mouse_y <= y + h

        if hovered or i == selected:
            pygame.draw.rect(screen, hover_color, (x - 4, y - 4, w + 8, h + 8), border_radius=8)
        pygame.draw.rect(screen, button_color, (x, y, w, h), border_radius=8)

        rect = font.render(game["name"], True, text_color).get_rect(center=(x + w // 2, y + h // 2))
        draw_text_with_outline(game["name"], rect.x, rect.y, text_color, (0, 0, 0))

    pygame.display.flip()


async def launch_game(module_name):
    global error_message
    try:
        mod = importlib.import_module(module_name)
        entry = getattr(mod, "main", None)
        if entry is None:
            raise AttributeError("modul nie ma funkcji main()")

        if asyncio.iscoroutinefunction(entry):
            await entry()
        else:
            entry()
        error_message = None
    except SystemExit:
        pass
    except Exception as e:
        error_message = f"Blad: {e}"
        print(f"Blad uruchamiania gry {module_name}: {e!r}")
    finally:
        restore_menu()


async def main():
    global selected
    load_assets()

    running = True
    while running:
        to_launch = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(games)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(games)
                elif event.key == pygame.K_RETURN:
                    to_launch = selected

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i in range(len(games)):
                    y1 = 320 + i * 60
                    if 160 <= mx <= 480 and y1 <= my <= y1 + 50:
                        selected = i
                        to_launch = i

        draw_menu()

        if to_launch is not None:
            await launch_game(games[to_launch]["module"])

        clock.tick(60)
        await asyncio.sleep(0)


asyncio.run(main())
