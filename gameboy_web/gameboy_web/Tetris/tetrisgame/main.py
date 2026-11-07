import asyncio
import platform
import pygame
from .tetris import Tetris
from .config import *

# --- WYSYLANIE WYNIKOW DO BACKENDU ---
API_URL = "http://127.0.0.1:8001"
TETRIS_ID = 2
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


def draw_score(win, font, score):
    score_text = font.render(f'Wynik: {score}', True, (255, 255, 255))
    win.blit(score_text, (10, 10))


def draw_game_over(win, font):
    msg = font.render('Game Over! Nacisnij ENTER by zrestartowac', True, (255, 0, 0))
    win.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))


async def main():
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    font = pygame.font.Font(None, 28)
    clock = pygame.time.Clock()
    pygame.key.set_repeat(150, 50)

    tetris = Tetris()
    score_sent = False

    try:
        while True:
            win.fill((0, 0, 0))
            tetris.draw(win)
            draw_score(win, font, tetris.score)

            if tetris.game_over:
                draw_game_over(win, font)
                # Wysylamy wynik tylko raz na koniec gry
                if not score_sent:
                    send_score(TETRIS_ID, tetris.score)
                    score_sent = True

            pygame.display.update()
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if tetris.game_over and event.key == pygame.K_RETURN:
                        tetris = Tetris()
                        score_sent = False
                    elif not tetris.game_over:
                        if event.key == pygame.K_LEFT:
                            tetris.move(-1)
                        elif event.key == pygame.K_RIGHT:
                            tetris.move(1)
                        elif event.key == pygame.K_DOWN:
                            tetris.soft_drop()
                        elif event.key == pygame.K_UP:
                            tetris.rotate()

            if not tetris.game_over:
                tetris.update()

            await asyncio.sleep(0)
    finally:
        pygame.key.set_repeat()