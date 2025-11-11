import pygame
import sys
import subprocess

pygame.init()

# === Nastavení ===
WIDTH, HEIGHT = 800, 600
BG_COLOR = (250, 240, 230)
BTN_COLOR = (230, 220, 200)
BTN_HOVER = (255, 230, 190)
TEXT_COLOR = (60, 40, 30)
FONT = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
SMALL_FONT = pygame.font.SysFont("Comic Sans MS", 28)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu | Color Warz")

clock = pygame.time.Clock()

# === Herní stavy ===
STATE_MAIN = "main"
STATE_PLAY = "play"
STATE_SETTINGS = "settings"
state = STATE_MAIN

volume_level = 0.5
slider_dragging = False


# === Pomocné funkce ===

def draw_button(text, x, y, w, h, action=None):
    """Vykreslí tlačítko a zkontroluje kliknutí."""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    rect = pygame.Rect(x, y, w, h)
    color = BTN_HOVER if rect.collidepoint(mouse) else BTN_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=20)

    label = FONT.render(text, True, TEXT_COLOR)
    screen.blit(label, label.get_rect(center=rect.center))

    if rect.collidepoint(mouse) and click[0]:
        pygame.time.delay(150)
        if action:
            action()


def launch_color_warz():
    """Spustí hru Color Warz."""
    cesta_hry = r"D:\Programování\Maturitka\Matěj_Linda\color_warz.py"  # celá cesta
    try:
        subprocess.Popen([sys.executable, cesta_hry])
    except Exception as e:
        print("❌ Nelze spustit Color Warz:", e)


# === Obrazovky ===

def main_menu():
    screen.fill(BG_COLOR)
    title = FONT.render("🎨 Hlavní Menu", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    draw_button("Hrát", WIDTH // 2 - 120, 220, 240, 70, action=lambda: change_state(STATE_PLAY))
    draw_button("Nastavení", WIDTH // 2 - 120, 320, 240, 70, action=lambda: change_state(STATE_SETTINGS))
    draw_button("Odejít", WIDTH // 2 - 120, 420, 240, 70, action=quit_game)


def play_menu():
    screen.fill(BG_COLOR)
    title = FONT.render("🎮 Vyber hru", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

    # Rámeček hry Color Warz
    game_rect = pygame.Rect(WIDTH // 2 - 150, 200, 300, 180)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    color = BTN_HOVER if game_rect.collidepoint(mouse) else BTN_COLOR
    pygame.draw.rect(screen, color, game_rect, border_radius=25)

    label = FONT.render("Color Warz", True, TEXT_COLOR)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 290)))

    if game_rect.collidepoint(mouse) and click[0]:
        pygame.time.delay(200)
        launch_color_warz()

    draw_button("Zpět", 30, HEIGHT - 80, 150, 50, action=lambda: change_state(STATE_MAIN))


def settings_menu():
    global volume_level, slider_dragging

    screen.fill(BG_COLOR)
    title = FONT.render("⚙️ Nastavení", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

    # Posuvník hlasitosti
    slider_rect = pygame.Rect(WIDTH // 2 - 150, 220, 300, 10)
    knob_x = slider_rect.x + int(volume_level * slider_rect.width)
    pygame.draw.rect(screen, (180, 160, 140), slider_rect)
    pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 12)
    label = SMALL_FONT.render("Hlasitost", True, TEXT_COLOR)
    screen.blit(label, (WIDTH // 2 - 60, 180))

    draw_button("Zpět", 30, HEIGHT - 80, 150, 50, action=lambda: change_state(STATE_MAIN))

    # Myš
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if click[0] and slider_rect.collidepoint(mouse):
        slider_dragging = True
    elif not click[0]:
        slider_dragging = False

    if slider_dragging:
        x = max(slider_rect.left, min(mouse[0], slider_rect.right))
        volume_level = (x - slider_rect.left) / slider_rect.width


def change_state(new_state):
    global state
    state = new_state


def quit_game():
    pygame.quit()
    sys.exit()


# === Hlavní smyčka ===
def main():
    global state
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        if state == STATE_MAIN:
            main_menu()
        elif state == STATE_PLAY:
            play_menu()
        elif state == STATE_SETTINGS:
            settings_menu()

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
