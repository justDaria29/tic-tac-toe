import pygame
import sys
import random
import tempfile
import subprocess

pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 3, 3
CELL_SIZE = WIDTH // COLS
LINE_WIDTH = 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (99, 204, 94)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")
screen.fill(GREEN)

FONT = pygame.font.SysFont('Helvetica', 80)
SMALL_FONT = pygame.font.SysFont('Helvetica', 40)

board = [["" for _ in range(COLS)] for _ in range(ROWS)]
player = "X"
computer = "O"
game_over = False

PROVER9_PATH = "prover9"

def draw_grid():
    for row in range(1, ROWS):
        pygame.draw.line(screen, BLACK, (0, row * CELL_SIZE), (WIDTH, row * CELL_SIZE), LINE_WIDTH)
    for col in range(1, COLS):
        pygame.draw.line(screen, BLACK, (col * CELL_SIZE, 0), (col * CELL_SIZE, HEIGHT), LINE_WIDTH)


def draw_moves():
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == "X":
                color = RED
                text = FONT.render("X", True, color)
            elif board[row][col] == "O":
                color = WHITE
                text = FONT.render("O", True, color)
            else:
                continue
            x = col * CELL_SIZE + CELL_SIZE // 2 - text.get_width() // 2
            y = row * CELL_SIZE + CELL_SIZE // 2 - text.get_height() // 2
            screen.blit(text, (x, y))

def generate_prover9_input():
    formulas = []

    for row in range(ROWS):
        for col in range(COLS):
            cell = f"_{row + 1}_{col + 1}"
            if board[row][col] == "X":
                formulas.append(f"X{cell}.")
            elif board[row][col] == "O":
                formulas.append(f"O{cell}.")
            else:
                formulas.append(f"Empty{cell}.")

    return "\n".join(formulas)

def query_prover9():
    """Query Prover9 to determine the computer's next move."""
    prover9_input = generate_prover9_input()

    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".in") as temp_file:
        temp_file.write(prover9_input)
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(["prover9", temp_file_path], capture_output=True, text=True, shell=True)
        output = result.stdout

        for line in output.splitlines():
            if line.startswith("ComputerMove"):
                move = line.split(" ")[1]
                row, col = int(move[1]) - 1, int(move[2]) - 1
                return row, col

    except Exception as e:
        print(f"Error running Prover9: {e}")
        return None


    
def check_winner():

    for i in range(ROWS):
        if board[i][0] == board[i][1] == board[i][2] != "":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != "":
            return board[0][i]

    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]

    for row in board:
        if "" in row:
            return None
    return "Draw"

def computer_move():
    move = query_prover9()

    if move is None:
        empty_cells = [(r, c) for r in range(ROWS) for c in range(COLS) if board[r][c] == ""]
        if empty_cells:
            move = random.choice(empty_cells)

    if move:
        row, col = move
        board[row][col] = computer



def reset_game():
    global board, game_over
    board = [["" for _ in range(COLS)] for _ in range(ROWS)]
    game_over = False
    screen.fill(GREEN)
    draw_grid()


def main():
    global game_over
    clock = pygame.time.Clock()
    draw_grid()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col, row = x // CELL_SIZE, y // CELL_SIZE
                if board[row][col] == "":
                    board[row][col] = player
                    winner = check_winner()
                    if winner:
                        game_over = True
                    else:
                        computer_move()
                        winner = check_winner()
                        if winner:
                            game_over = True

            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    reset_game()

        draw_grid()
        draw_moves()

        if game_over:
            winner = check_winner()
            if winner == "Draw":
                text = SMALL_FONT.render("It's a Draw! Press 'R' to Restart", True, BLACK)
            else:
                text = SMALL_FONT.render(f"{winner} Wins! Press 'R' to Restart", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
