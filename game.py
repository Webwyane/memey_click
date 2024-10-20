import pygame
import random

# Constants
WIDTH, HEIGHT = 540, 600
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Sudoku class
class Sudoku:
    def __init__(self):
        self.grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.generate_puzzle()

    def generate_puzzle(self):
        self.fill_grid()
        self.remove_numbers()

    def fill_grid(self):
        self._fill(0, 0)

    def _fill(self, row, col):
        if row == GRID_SIZE:
            return True
        if col == GRID_SIZE:
            return self._fill(row + 1, 0)
        if self.grid[row][col] != 0:
            return self._fill(row, col + 1)

        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for num in numbers:
            if self.is_safe(row, col, num):
                self.grid[row][col] = num
                if self._fill(row, col + 1):
                    return True
                self.grid[row][col] = 0
        return False

    def is_safe(self, row, col, num):
        # Check row and column
        for i in range(GRID_SIZE):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False

        # Check 3x3 grid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.grid[start_row + i][start_col + j] == num:
                    return False
        return True

    def remove_numbers(self, difficulty=0.5):
        count = int(GRID_SIZE * GRID_SIZE * difficulty)
        while count > 0:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            if self.grid[row][col] != 0:
                self.grid[row][col] = 0
                count -= 1

# Game class
class SudokuGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku")
        self.clock = pygame.time.Clock()
        self.sudoku = Sudoku()
        self.selected = None
        self.input_num = ''
        self.running = True

    def draw_grid(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                pygame.draw.rect(self.screen, WHITE, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                if self.sudoku.grid[i][j] != 0:
                    font = pygame.font.Font(None, 40)
                    text = font.render(str(self.sudoku.grid[i][j]), True, BLACK)
                    self.screen.blit(text, (j * CELL_SIZE + CELL_SIZE // 4, i * CELL_SIZE + CELL_SIZE // 4))

                if (i + j) % 3 == 0:
                    pygame.draw.rect(self.screen, DARK_GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
                else:
                    pygame.draw.rect(self.screen, LIGHT_GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def run(self):
        while self.running:
            self.screen.fill(BLACK)
            self.draw_grid()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key in range(pygame.K_1, pygame.K_9 + 1):
                        self.input_num = str(event.key - pygame.K_0)
                    if event.key == pygame.K_RETURN and self.selected and self.input_num:
                        row, col = self.selected
                        if self.sudoku.is_safe(row, col, int(self.input_num)):
                            self.sudoku.grid[row][col] = int(self.input_num)
                        self.input_num = ''
                    if event.key == pygame.K_BACKSPACE:
                        if self.selected:
                            row, col = self.selected
                            self.sudoku.grid[row][col] = 0

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if x < WIDTH and y < HEIGHT - 60:
                        self.selected = (y // CELL_SIZE, x // CELL_SIZE)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = SudokuGame()
    game.run()
