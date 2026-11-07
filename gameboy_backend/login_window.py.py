import pygame
import sys
from api_client import APIClient

def run_login_screen():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Gameboy - Logowanie")
    
    font = pygame.font.Font(None, 32)
    client = APIClient() 
    username = ""
    password = ""
    active_field = "username"
    message = ""
    message_color = (255, 0, 0)

    running = True
    logged_in = False

    while running:
        screen.fill((30, 30, 30))
        
        
        title_surf = font.render("Logowanie do Gameboy", True, (255, 255, 255))
        screen.blit(title_surf, (80, 30))

        # Pole Username
        user_label = font.render("Login:", True, (200, 200, 200))
        screen.blit(user_label, (50, 90))
        user_box = pygame.Rect(50, 120, 300, 35)
        pygame.draw.rect(screen, (255, 255, 255) if active_field == "username" else (100, 100, 100), user_box, 2)
        user_text = font.render(username, True, (255, 255, 255))
        screen.blit(user_text, (user_box.x + 5, user_box.y + 5))

        # Pole Password
        pass_label = font.render("Hasło:", True, (200, 200, 200))
        screen.blit(pass_label, (50, 165))
        pass_box = pygame.Rect(50, 195, 300, 35)
        pygame.draw.rect(screen, (255, 255, 255) if active_field == "password" else (100, 100, 100), pass_box, 2)
        pass_masked = "*" * len(password)
        pass_text = font.render(pass_masked, True, (255, 255, 255))
        screen.blit(pass_text, (pass_box.x + 5, pass_box.y + 5))

        # Komunikat zwrotny
        if message:
            msg_surf = font.render(message, True, message_color)
            screen.blit(msg_surf, (50, 240))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if user_box.collidepoint(event.pos):
                    active_field = "username"
                elif pass_box.collidepoint(event.pos):
                    active_field = "password"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Próba logowania po naciśnięciu Enter
                    success, msg = client.login(username, password)
                    message = msg
                    if success:
                        message_color = (0, 255, 0)
                        pygame.display.flip()
                        pygame.time.delay(1000) 
                        return client 
                    else:
                        message_color = (255, 0, 0)
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    if event.unicode.isprintable():
                        if active_field == "username":
                            username += event.unicode
                        else:
                            password += event.unicode

    return None

if __name__ == "__main__":
    api_client = run_login_screen()
    if api_client:
        print(f"Zalogowano pomyślnie jako: {api_client.username} (ID: {api_client.user_id})")
        