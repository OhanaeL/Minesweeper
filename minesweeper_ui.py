import pygame
import numpy as np
from minesweeper_env import MinesweeperEnv
from minesweeper_solver import MinesweeperSolver
import time
import os


class MinesweeperGUI:
    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.env = MinesweeperEnv(rows, cols, mines)
        self.solver = MinesweeperSolver(rows, cols, mines)

        self.cell_size = 32
        self.margin = 2
        self.width = cols * (self.cell_size + self.margin) + 60
        self.height = rows * (self.cell_size + self.margin) + 140

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper Solver")
        self.clock = pygame.time.Clock()

        font_path = os.path.join("assets", "font", "upheaval", "upheavtt.ttf")
        try:
            # upheaval font
            self.font = pygame.font.Font(font_path, 24)
            self.title_font = pygame.font.Font(font_path, 24)
            self.number_font = pygame.font.Font(font_path, 32)
            self.small_font = pygame.font.Font(font_path, 18)
            self.button_font = pygame.font.Font(font_path, 22)
        except:
            try:
                self.font = pygame.font.Font(pygame.font.get_default_font(), 18)
                self.title_font = pygame.font.Font(pygame.font.get_default_font(), 18)
                self.number_font = pygame.font.Font(pygame.font.get_default_font(), 24)
                self.small_font = pygame.font.Font(pygame.font.get_default_font(), 14)
                self.button_font = pygame.font.Font(pygame.font.get_default_font(), 16)
            except:
                self.font = pygame.font.Font(None, 18)
                self.title_font = pygame.font.Font(None, 18)
                self.number_font = pygame.font.Font(None, 24)
                self.small_font = pygame.font.Font(None, 14)
                self.button_font = pygame.font.Font(None, 16)

        self.solving = False
        self.auto_step = True
        self.move_delay = 0.1

        button_width = 200
        button_height = 50
        self.button_rect = pygame.Rect(self.width - button_width - 20, 20, button_width, button_height)

        self.colors = {
            'bg': (240, 240, 240),
            'unrevealed': (200, 200, 200),
            'unrevealed_border': (160, 160, 160),
            'revealed': (250, 250, 250),
            'revealed_border': (200, 200, 200),
            'flag': (255, 220, 0),
            'flag_border': (200, 170, 0),
            'mine': (200, 0, 0),
            'mine_border': (150, 0, 0),
            'exploded': (255, 0, 0),
            'exploded_border': (200, 0, 0),
            'button': (70, 130, 180),
            'button_hover': (100, 160, 210),
            'button_active': (50, 100, 150),
            'text': (30, 30, 30),
            'text_light': (120, 120, 120),
            'won': (50, 180, 50),
            'lost': (220, 50, 50),
            'numbers': {
                1: (0, 0, 220),
                2: (0, 150, 0),
                3: (220, 0, 0),
                4: (140, 0, 180),
                5: (180, 0, 0),
                6: (0, 150, 150),
                7: (0, 0, 0),
                8: (100, 100, 100),
            }
        }

    def draw_board(self):
        self.screen.fill(self.colors['bg'])
        board = self.env.board_state()
        game_state = self.env.game_state()

        # if lost, reveal all mines
        if game_state == "lost":
            self.env.reveal_all_mines()
            board = self.env.board_state()

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * (self.cell_size + self.margin) + 30
                y = row * (self.cell_size + self.margin) + 80

                val = board[row, col]
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                if val == -1:
                    pygame.draw.rect(self.screen, self.colors['unrevealed'], rect)
                    pygame.draw.rect(self.screen, self.colors['unrevealed_border'], rect, 2)
                    pygame.draw.line(self.screen, (230, 230, 230), (x, y), (x + self.cell_size - 2, y), 1)
                    pygame.draw.line(self.screen, (230, 230, 230), (x, y), (x, y + self.cell_size - 2), 1)
                elif val == 9:
                    pygame.draw.rect(self.screen, self.colors['flag'], rect)
                    pygame.draw.rect(self.screen, self.colors['flag_border'], rect, 2)
                    flag_text = self.number_font.render("F", True, (0, 0, 0))
                    text_rect = flag_text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    self.screen.blit(flag_text, text_rect)
                elif val == 10:
                    pygame.draw.rect(self.screen, self.colors['mine'], rect)
                    pygame.draw.rect(self.screen, self.colors['mine_border'], rect, 2)
                    mine_text = self.number_font.render("M", True, (255, 255, 255))
                    text_rect = mine_text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    self.screen.blit(mine_text, text_rect)
                elif val == 11:
                    pygame.draw.rect(self.screen, self.colors['exploded'], rect)
                    pygame.draw.rect(self.screen, self.colors['exploded_border'], rect, 3)
                    explode_text = self.number_font.render("X", True, (255, 255, 255))
                    text_rect = explode_text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    self.screen.blit(explode_text, text_rect)
                else:
                    pygame.draw.rect(self.screen, self.colors['revealed'], rect)
                    pygame.draw.rect(self.screen, self.colors['revealed_border'], rect, 1)
                    if val > 0:
                        color = self.colors['numbers'].get(val, (0, 0, 0))
                        text = self.number_font.render(str(val), True, color)
                        text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                        self.screen.blit(text, text_rect)

        revealed = np.sum(self.env.revealed)
        total = self.rows * self.cols
        flagged_count = np.sum(self.env.flagged)
        remaining_mines = self.mines - flagged_count

        if game_state == "won":
            status_text = "VICTORY!"
            color = self.colors['won']
        elif game_state == "lost":
            status_text = "GAME OVER!"
            color = self.colors['lost']
        else:
            if self.solving:
                status_text = f"Solving... {revealed}/{total - self.mines} revealed"
            else:
                status_text = f"Ready - {revealed}/{total - self.mines} revealed"
            color = self.colors['text']

        # status text with better positioning
        text_surface = self.title_font.render(status_text, True, color)
        text_y = self.button_rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (30, text_y))

        # flags | mines counter display
        mines_text = f"Flags: {flagged_count} | Remaining: {remaining_mines}"
        mines_surface = self.small_font.render(mines_text, True, self.colors['text'])
        mines_y = text_y + text_surface.get_height() + 4
        self.screen.blit(mines_surface, (30, mines_y))

        mouse_pos = pygame.mouse.get_pos()
        button_hover = self.button_rect.collidepoint(mouse_pos)

        if self.solving:
            button_color = self.colors['button_active']
        elif button_hover:
            button_color = self.colors['button_hover']
        else:
            button_color = self.colors['button']

        shadow_rect = pygame.Rect(self.button_rect.x + 2, self.button_rect.y + 2, self.button_rect.width, self.button_rect.height)
        pygame.draw.rect(self.screen, (30, 30, 30, 50), shadow_rect, border_radius=8)

        # main button
        pygame.draw.rect(self.screen, button_color, self.button_rect, width=0, border_radius=8)
        pygame.draw.rect(self.screen, (40, 40, 40), self.button_rect, width=3, border_radius=8)

        # button text
        button_text = "START SOLVING" if not self.solving else "SOLVING..."
        text_surface = self.button_font.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(text_surface, text_rect)

        # help text
        help_text = "SPACE: STEP | A: AUTO | R: RESET | ESC: QUIT"
        help_surface = self.small_font.render(help_text, True, self.colors['text_light'])
        help_y = self.height - help_surface.get_height() - 15
        self.screen.blit(help_surface, (30, help_y))

        pygame.display.flip()

    def solve_step(self):
        if not self.solving:
            return

        board = self.env.board_state()
        game_state_str = self.env.game_state()

        if game_state_str != "playing":
            self.solving = False
            if game_state_str == "won":
                self.env.reveal_remaining_mines()
            self.draw_board()
            return

        action = self.solver.get_action(board, game_state_str)

        if action is None:
            self.solving = False
            if self.env.game_state() == "won":
                self.env.reveal_remaining_mines()
            self.draw_board()
            return

        action_type, (row, col) = action

        if action_type == "click":
            self.env.click_cell(row, col)
            if self.env.game_state() == "won":
                self.env.reveal_remaining_mines()
        elif action_type == "flag":
            self.env.flag_cell(row, col)
            self.solver.update_flag(row, col, True)

        self.draw_board()

        if self.auto_step:
            time.sleep(self.move_delay)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_rect.collidepoint(event.pos):
                        if not self.solving:
                            self.start_solving()
                        else:
                            self.auto_step = not self.auto_step

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.solving:
                        self.start_solving()
                    else:
                        self.solve_step()
                elif event.key == pygame.K_a:
                    self.auto_step = not self.auto_step
                    if self.auto_step and not self.solving:
                        self.start_solving()
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False

        if self.auto_step and self.solving:
            self.solve_step()

        return True

    def start_solving(self):
        if self.env.game_state() != "playing":
            self.reset_game()

        first_row = self.rows // 2
        first_col = self.cols // 2
        self.env.click_cell(first_row, first_col)
        self.solving = True
        self.draw_board()

    def reset_game(self):
        self.env.reset()
        self.solver.reset()
        self.solving = False
        self.auto_step = True
        self.draw_board()

    def run(self):
        self.draw_board()
        running = True

        while running:
            running = self.handle_events()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        rows = int(sys.argv[1])
        cols = int(sys.argv[2])
        mines = int(sys.argv[3])
    else:
        difficulty = input("Difficulty? (easy/intermediate/expert): ").strip().lower()
        difficulty_configs = {
            "easy": (9, 9, 10),
            "intermediate": (16, 16, 40),
            "expert": (16, 30, 99),
        }

        if difficulty not in difficulty_configs:
            print("Invalid difficulty. Using intermediate")
            difficulty = "intermediate"

        rows, cols, mines = difficulty_configs[difficulty]

    gui = MinesweeperGUI(rows, cols, mines)
    gui.run()
