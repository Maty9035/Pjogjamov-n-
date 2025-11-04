import pygame
import sys

pygame.init()

# Nastavení
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 6, 6
CELL_SIZE = WIDTH // COLS

# Barvy
BG_COLOR = (255, 245, 235)
LINE_COLOR = (200, 180, 150)
PLAYER_COLORS = [(235, 100, 100), (100, 160, 235)]
DOT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Warz")

font = pygame.font.SysFont(None, 36)
win_font = pygame.font.SysFont("Comic Sans MS", 80, bold=True)

# Data pro každé pole: {'owner': 0/1/None, 'dots': int}
board = [[{'owner': None, 'dots': 0} for _ in range(COLS)] for _ in range(ROWS)]

current_player = 0
starting_phase = True
starting_positions_selected = [False, False]
game_over = False
winner = None
scores = [0, 0]


def draw_board():
    screen.fill(BG_COLOR)

    # --- Mřížka s jemnými, tlustšími a zakulacenými okraji ---
    border_thickness = 4
    border_radius = 12
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(
                c * CELL_SIZE + 1,
                r * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
            pygame.draw.rect(screen, LINE_COLOR, rect, width=border_thickness, border_radius=border_radius)

    # --- Kreslení buněk a teček ---
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if cell['owner'] is not None:
                # Kulatý barevný blok
                center = (c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2)
                radius = CELL_SIZE // 2 - 10
                pygame.draw.circle(screen, PLAYER_COLORS[cell['owner']], center, radius)

                # Tečky jako na kostce 🎲
                dot_positions = []
                offset = 12
                cx, cy = center

                if cell['dots'] == 1:
                    dot_positions = [(cx, cy)]
                elif cell['dots'] == 2:
                    dot_positions = [(cx - offset, cy - offset), (cx + offset, cy + offset)]
                elif cell['dots'] == 3:
                    dot_positions = [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)]
                elif cell['dots'] == 4:
                    dot_positions = [
                        (cx - offset, cy - offset),
                        (cx + offset, cy - offset),
                        (cx - offset, cy + offset),
                        (cx + offset, cy + offset)
                    ]

                for pos in dot_positions:
                    pygame.draw.circle(screen, DOT_COLOR, pos, 6)

    # --- Text kdo je na tahu ---
    if not game_over:
        if starting_phase:
            text = font.render(f"Hráč {current_player + 1} zvol startovní pozici", True, (50, 50, 50))
        else:
            text = font.render(f"Hráč {current_player + 1} je na tahu", True, (50, 50, 50))
        screen.blit(text, (10, HEIGHT - 40))


def neighbors(r, c):
    for nr, nc in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield nr, nc


def explode(r, c):
    cell = board[r][c]
    if cell['dots'] < 4:
        return
    cell['dots'] = 1
    for nr, nc in neighbors(r, c):
        neighbor_cell = board[nr][nc]
        neighbor_cell['dots'] += 1
        neighbor_cell['owner'] = cell['owner']
        if neighbor_cell['dots'] >= 4:
            explode(nr, nc)


def can_place(r, c, player):
    cell = board[r][c]
    return cell['owner'] == player


def place_dot(r, c, player):
    if not can_place(r, c, player):
        return False
    board[r][c]['dots'] += 1
    explode(r, c)
    return True


def check_winner():
    owners = set()
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]['owner'] is not None:
                owners.add(board[r][c]['owner'])
    if len(owners) == 1:
        return owners.pop()
    return None


def handle_starting_position(r, c):
    global current_player, starting_phase
    cell = board[r][c]
    if cell['owner'] is None:
        board[r][c] = {'owner': current_player, 'dots': 3}
        starting_positions_selected[current_player] = True
        if all(starting_positions_selected):
            starting_phase = False
            current_player = 0
        else:
            current_player = 1 - current_player


def reset_game():
    global board, starting_phase, starting_positions_selected, current_player, game_over, winner
    board = [[{'owner': None, 'dots': 0} for _ in range(COLS)] for _ in range(ROWS)]
    starting_phase = True
    starting_positions_selected = [False, False]
    current_player = 0
    game_over = False
    winner = None

def show_winner_effect(winner):
    global game_over
    clock = pygame.time.Clock()

    # --- Nejprve necháme hráče vidět poslední tah 3 sekundy ---
    draw_board()
    pygame.display.flip()
    pygame.time.delay(1000)  # 1 sekunda

    # --- Efekt pomalého stmavení / rozmazání pozadí ---
    blur_surface = screen.copy()
    for alpha in range(0, 160, 8):
        blur = pygame.Surface((WIDTH, HEIGHT))
        blur.fill((0, 0, 0))
        blur.set_alpha(alpha)
        screen.blit(blur_surface, (0, 0))
        screen.blit(blur, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    # --- Vykreslení výsledku ---
    win_text = win_font.render(f"Hráč {winner + 1} vyhrál!", True, PLAYER_COLORS[winner])
    text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(win_text, text_rect)

    # Tlačítko Restart
    restart_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 20, 160, 60)
    pygame.draw.rect(screen, LINE_COLOR, restart_rect, border_radius=15)
    pygame.draw.rect(screen, PLAYER_COLORS[winner], restart_rect, width=4, border_radius=15)
    restart_text = font.render("Restart", True, PLAYER_COLORS[winner])
    text_pos = restart_text.get_rect(center=restart_rect.center)
    screen.blit(restart_text, text_pos)

    # Skóre
    score_text = font.render(f"{scores[0]} : {scores[1]}", True, (230, 230, 230))
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(score_text, score_rect)

    pygame.display.flip()

    # --- Čekání na kliknutí na restart ---
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if restart_rect.collidepoint(x, y):
                    waiting = False
                    reset_game()

    game_over = False    

def main():
    global current_player, game_over, winner

    clock = pygame.time.Clock()
    running = True

    while running:
        draw_board()
        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                c = x // CELL_SIZE
                r = y // CELL_SIZE

                if not game_over:
                    if starting_phase:
                        handle_starting_position(r, c)
                    else:
                        if place_dot(r, c, current_player):
                            current_player = 1 - current_player
                            winner = check_winner()
                            if winner is not None:
                                scores[winner] += 1
                                game_over = True
                                show_winner_effect(winner)
                else:
                    # kliknutí na restart během game_over
                    x, y = pygame.mouse.get_pos()
                    if restart_button.collidepoint(x, y):
                        reset_game()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

