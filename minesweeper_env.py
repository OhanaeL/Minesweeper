import random
import numpy as np
from typing import Tuple


class MinesweeperEnv:
    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.reset()

    def reset(self):
        self.mine_positions = set()
        self.revealed = np.zeros((self.rows, self.cols), dtype=bool)
        self.flagged = np.zeros((self.rows, self.cols), dtype=bool)
        self.board = np.full((self.rows, self.cols), -1)
        self.game_over = False
        self.won = False
        self.exploded_mine = None

    def _place_mines(self, first_click_row: int, first_click_col: int):
        excluded = set()
        for r in range(max(0, first_click_row - 1), min(self.rows, first_click_row + 2)):
            for c in range(max(0, first_click_col - 1), min(self.cols, first_click_col + 2)):
                excluded.add((r, c))

        available = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) not in excluded]
        self.mine_positions = set(random.sample(available, min(self.mines, len(available))))

    def _count_adjacent_mines(self, row: int, col: int) -> int:
        count = 0
        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                if (r, c) in self.mine_positions:
                    count += 1
        return count

    def _reveal_cell(self, row: int, col: int):
        if self.revealed[row, col] or self.flagged[row, col]:
            return

        self.revealed[row, col] = True

        if (row, col) in self.mine_positions:
            self.board[row, col] = 11
            self.exploded_mine = (row, col)
            self.game_over = True
            self.won = False
            return

        count = self._count_adjacent_mines(row, col)
        self.board[row, col] = count

        if count == 0:
            for r in range(max(0, row - 1), min(self.rows, row + 2)):
                for c in range(max(0, col - 1), min(self.cols, col + 2)):
                    if not self.revealed[r, c] and not self.flagged[r, c]:
                        self._reveal_cell(r, c)

    def click_cell(self, row: int, col: int) -> Tuple[np.ndarray, bool, bool]:
        if self.game_over:
            return self.board, False, True

        if not self.mine_positions:
            self._place_mines(row, col)

        if self.flagged[row, col]:
            return self.board, False, self.game_over

        self._reveal_cell(row, col)

        if not self.game_over:
            total_cells = self.rows * self.cols
            revealed_count = np.sum(self.revealed)
            if revealed_count == total_cells - self.mines:
                self.game_over = True
                self.won = True

        return self.board.copy(), self.won, self.game_over

    def flag_cell(self, row: int, col: int):
        if self.game_over or self.revealed[row, col]:
            return

        self.flagged[row, col] = not self.flagged[row, col]
        if self.flagged[row, col]:
            self.board[row, col] = 9
        else:
            self.board[row, col] = -1

    def board_state(self) -> np.ndarray:
        return self.board.copy()

    def reveal_remaining_mines(self):
        if not self.won:
            return

        for row in range(self.rows):
            for col in range(self.cols):
                if not self.revealed[row, col] and not self.flagged[row, col]:
                    if (row, col) in self.mine_positions:
                        self.flagged[row, col] = True
                        self.board[row, col] = 9

    def reveal_all_mines(self):
        if not self.game_over or self.won:
            return

        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) in self.mine_positions:
                    if not self.revealed[row, col]:
                        if (row, col) == self.exploded_mine:
                            self.board[row, col] = 11
                        else:
                            self.board[row, col] = 10

    def game_state(self) -> str:
        if self.game_over:
            return "won" if self.won else "lost"
        return "playing"

