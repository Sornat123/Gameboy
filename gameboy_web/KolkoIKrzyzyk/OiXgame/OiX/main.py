import asyncio
import pygame
import platform

from .board import Board
from .ai import get_ai_move
from .exceptions import InvalidMoveError


WIDTH, HEIGHT = 500, 600
WHITE = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (120, 120, 120)

OFFSET_X = (WIDTH - 300) // 2
OFFSET_Y = 80

GAME_ID = 4
GAME_DURATION = 60
ROUND_DELAY = 700

API_URL = "http://127.0.0.1:8001"

_token = None


def get_token():
    global _token

    if _token:
        return _token

    try:
        url_hash = platform.window.location.hash

        if "token=" in url_hash:
            _token = url_hash.split("token=", 1)[1].split("&", 1)[0]

        return _token

    except Exception:
        return None


def send_score(game_id, score):
    token = get_token()

    if not token:
        print("Nie znaleziono tokenu użytkownika.")
        return

    try:
        js = f"""
        fetch('{API_URL}/api/scores', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {token}'
            }},
            body: JSON.stringify({{
                game_id: {int(game_id)},
                score: {int(score)}
            }})
        }})
        .then(response => response.json())
        .then(data => console.log('Wynik zapisany:', data))
        .catch(error => console.error('Błąd zapisu wyniku:', error));
        """

        platform.window.eval(js)

    except Exception as e:
        print("Błąd wysyłania wyniku:", e)


def draw_board(screen, board, font):
    screen.fill(WHITE)

    for i in range(1, 3):
        pygame.draw.line(
            screen,
            LINE_COLOR,
            (OFFSET_X, OFFSET_Y + i * 100),
            (OFFSET_X + 300, OFFSET_Y + i * 100),
            3
        )

        pygame.draw.line(
            screen,
            LINE_COLOR,
            (OFFSET_X + i * 100, OFFSET_Y),
            (OFFSET_X + i * 100, OFFSET_Y + 300),
            3
        )

    for row in range(3):
        for col in range(3):
            mark = board.board[row][col]

            if mark != ' ':
                text = font.render(mark, True, LINE_COLOR)

                screen.blit(
                    text,
                    (OFFSET_X + col * 100 + 30,
                     OFFSET_Y + row * 100 + 15)
                )


def draw_menu(screen, font, menu_font):
    screen.fill(WHITE)

    title = font.render("Kółko i Krzyżyk", True, LINE_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    ai_btn = menu_font.render("1. Zagraj z AI", True, LINE_COLOR)
    two_btn = menu_font.render("2. Zagraj z graczem", True, LINE_COLOR)
    esc_btn = menu_font.render("ESC - wróć do menu", True, GRAY)

    screen.blit(ai_btn, (WIDTH // 2 - ai_btn.get_width() // 2, 200))
    screen.blit(two_btn, (WIDTH // 2 - two_btn.get_width() // 2, 250))
    screen.blit(esc_btn, (WIDTH // 2 - esc_btn.get_width() // 2, 400))


def draw_winner(screen, info_font, winner, ai_mode=False):
    message = "Remis!" if winner == "Remis" else f"Wygrał {winner}!"

    if ai_mode:
        message += " Następna runda..."
    else:
        message += " Naciśnij R, aby zagrać ponownie."

    text = info_font.render(message, True, RED)

    screen.blit(
        text,
        (WIDTH // 2 - text.get_width() // 2, OFFSET_Y + 320)
    )


def draw_ai_info(screen, info_font, remaining_time, score):
    time_text = info_font.render(
        f"Czas: {remaining_time}s",
        True,
        LINE_COLOR
    )

    score_text = info_font.render(
        f"Punkty: {score}",
        True,
        LINE_COLOR
    )

    screen.blit(time_text, (80, 25))
    screen.blit(score_text, (320, 25))


async def menu_loop(screen, font, menu_font):
    while True:
        draw_menu(screen, font, menu_font)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return True

                if event.key == pygame.K_2:
                    return False

                if event.key == pygame.K_ESCAPE:
                    return None

        await asyncio.sleep(0)


async def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kółko i Krzyżyk")

    font = pygame.font.Font(None, 60)
    menu_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 28)

    clock = pygame.time.Clock()

    ai_mode = await menu_loop(screen, font, menu_font)

    if ai_mode is None:
        return

    board = Board()
    player = 'X'
    winner = None

    # Dane trybu czasowego AI
    score = 0
    start_time = pygame.time.get_ticks()
    session_finished = False
    score_sent = False
    round_finished_time = None

    while True:
        current_time = pygame.time.get_ticks()

        elapsed_time = (current_time - start_time) // 1000
        remaining_time = max(0, GAME_DURATION - elapsed_time)

        # Koniec trybu czasowego
        if ai_mode and remaining_time <= 0 and not session_finished:
            session_finished = True

            if not score_sent:
                send_score(GAME_ID, score)
                score_sent = True

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    return

                # Restart sesji czasowej AI
                if event.key == pygame.K_r and ai_mode and session_finished:
                    board.reset()
                    player = 'X'
                    winner = None

                    score = 0
                    start_time = pygame.time.get_ticks()

                    session_finished = False
                    score_sent = False
                    round_finished_time = None

                # Dotychczasowy restart gry dla dwóch graczy
                elif event.key == pygame.K_r and not ai_mode and winner:
                    board.reset()
                    player = 'X'
                    winner = None

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and not winner
                and not session_finished
                and not (ai_mode and player == 'O')
            ):

                x, y = event.pos

                if (
                    OFFSET_X <= x < OFFSET_X + 300
                    and OFFSET_Y <= y < OFFSET_Y + 300
                ):

                    row = (y - OFFSET_Y) // 100
                    col = (x - OFFSET_X) // 100

                    try:
                        board.make_move(row, col, player)

                        player = 'O' if player == 'X' else 'X'

                    except InvalidMoveError:
                        pass

        # Sprawdzenie zwycięzcy
        if not winner and not session_finished:
            winner = board.check_winner()

        # Ruch AI
        if (
            not winner
            and not session_finished
            and ai_mode
            and player == 'O'
        ):

            try:
                move = get_ai_move(board)

                if move is not None:
                    row, col = move
                    board.make_move(row, col, 'O')
                    player = 'X'

            except InvalidMoveError:
                pass

            winner = board.check_winner()

        # Naliczanie punktów i oczekiwanie na następną rundę
        if ai_mode and winner and not session_finished:

            if round_finished_time is None:

                if winner == 'X':
                    score += 3

                elif winner == 'Remis':
                    score += 1

                round_finished_time = pygame.time.get_ticks()

            elif current_time - round_finished_time >= ROUND_DELAY:

                board.reset()
                player = 'X'
                winner = None
                round_finished_time = None

        # Rysowanie planszy
        draw_board(screen, board, font)

        if ai_mode:
            draw_ai_info(screen, info_font, remaining_time, score)

        if winner:
            draw_winner(screen, info_font, winner, ai_mode)

        # Ekran końcowy trybu AI
        if ai_mode and session_finished:

            screen.fill(WHITE)

            title = font.render("Koniec czasu!", True, RED)
            points = info_font.render(
                f"Zdobyte punkty: {score}",
                True,
                LINE_COLOR
            )

            restart = info_font.render(
                "R - zagraj ponownie",
                True,
                LINE_COLOR
            )

            esc = info_font.render(
                "ESC - wyjdz",
                True,
                GRAY
            )

            screen.blit(
                title,
                (WIDTH // 2 - title.get_width() // 2, 170)
            )

            screen.blit(
                points,
                (WIDTH // 2 - points.get_width() // 2, 260)
            )

            screen.blit(
                restart,
                (WIDTH // 2 - restart.get_width() // 2, 340)
            )

            screen.blit(
                esc,
                (WIDTH // 2 - esc.get_width() // 2, 390)
            )

        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)