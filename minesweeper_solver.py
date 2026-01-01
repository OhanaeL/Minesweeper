import random
import time

import numpy as np

from collections import defaultdict
from typing import List, Tuple

class MinesweeperSolver:

    def __init__(self, rows: int, cols: int, mines: int):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.flagged = set()
        self._neighbor_cache = {}

    def get_neighbours(self, row: int, col: int):
        cache_key = (row, col)
        if cache_key in self._neighbor_cache:
            return self._neighbor_cache[cache_key]
        
        neighbours = []
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue
                neighbour_row = row + row_offset
                neighbour_col = col + col_offset
                if 0 <= neighbour_row < self.rows and 0 <= neighbour_col < self.cols:
                    neighbours.append((neighbour_row, neighbour_col))
        
        self._neighbor_cache[cache_key] = neighbours
        return neighbours

    def _analyze_constraints(self, board: np.ndarray):
        safe_cells = []
        mine_cells = []
        
        revealed_mask = (board >= 0) & (board <= 8)
        revealed_positions = np.argwhere(revealed_mask)
        
        for row, col in revealed_positions:
            cell_value = board[row, col]
            neighbours = self.get_neighbours(row, col)
            unrevealed_neighbours = []
            flagged_count = 0

            for neighbour_row, neighbour_col in neighbours:
                if (neighbour_row, neighbour_col) in self.flagged:
                    flagged_count += 1
                elif board[neighbour_row, neighbour_col] == -1:
                    unrevealed_neighbours.append((neighbour_row, neighbour_col))

            remaining_mines = cell_value - flagged_count
            
            if flagged_count == cell_value and unrevealed_neighbours:
                safe_cells.extend(unrevealed_neighbours)
            elif remaining_mines > 0 and len(unrevealed_neighbours) == remaining_mines:
                mine_cells.extend(unrevealed_neighbours)
        
        return safe_cells, mine_cells

    def find_guaranteed_safe_cells(self, board: np.ndarray):
        safe_cells, _ = self._analyze_constraints(board)
        return safe_cells

    def find_guaranteed_mines(self, board: np.ndarray):
        _, mine_cells = self._analyze_constraints(board)
        return mine_cells

    def calculate_probabilities(self, board: np.ndarray):
        probabilities = defaultdict(lambda: [0, 0])
        
        revealed_mask = (board >= 0) & (board <= 8)
        revealed_positions = np.argwhere(revealed_mask)

        for row, col in revealed_positions:
            cell_value = board[row, col]
            neighbours = self.get_neighbours(row, col)
            unrevealed_neighbours = []
            flagged_count = 0

            for neighbour_row, neighbour_col in neighbours:
                if (neighbour_row, neighbour_col) in self.flagged:
                    flagged_count += 1
                elif board[neighbour_row, neighbour_col] == -1:
                    unrevealed_neighbours.append((neighbour_row, neighbour_col))

            remaining_mines = cell_value - flagged_count
            if remaining_mines > 0 and unrevealed_neighbours:
                for neighbour_row, neighbour_col in unrevealed_neighbours:
                    probabilities[(neighbour_row, neighbour_col)][0] += remaining_mines
                    probabilities[(neighbour_row, neighbour_col)][1] += len(unrevealed_neighbours)

        prob_dict = {}
        for cell, (mine_sum, constraint_sum) in probabilities.items():
            if constraint_sum > 0:
                prob_dict[cell] = mine_sum / constraint_sum
            else:
                prob_dict[cell] = 0.5

        return prob_dict

    def _is_early_game(self, board: np.ndarray) -> bool:
        revealed_mask = (board >= 0) & (board <= 8)
        revealed_count = np.sum(revealed_mask)
        has_zero = np.any(board == 0)
        return revealed_count < 10 and not has_zero

    def _get_cell_far_from_revealed(self, board: np.ndarray, unknown_cells: List[Tuple[int, int]]) -> Tuple[int, int]:
        revealed_mask = (board >= 0) & (board <= 8)
        revealed_positions = np.argwhere(revealed_mask)

        if len(revealed_positions) == 0:
            return random.choice(unknown_cells)

        best_cell = None
        max_distance = -1

        for cell in unknown_cells:
            cell_pos = np.array([cell[0], cell[1]])
            distances = np.abs(revealed_positions - cell_pos)
            min_dist_to_revealed = np.min(np.sum(distances, axis=1))
            if min_dist_to_revealed > max_distance:
                max_distance = min_dist_to_revealed
                best_cell = cell

        return best_cell if best_cell else random.choice(unknown_cells)

    def get_action(self, board, game_state):
        if game_state != "playing":
            return None

        safe, mines = self._analyze_constraints(board)
        
        if safe:
            best_safe_cell = self._prefer_informative_cell(board, safe)
            return ("click", best_safe_cell)

        if mines:
            return ("flag_all", mines)

        unknown_cells = self._get_unknown_cells(board)
        if not unknown_cells:
            return None

        if self._is_early_game(board):
            far_cell = self._get_cell_far_from_revealed(board, unknown_cells)
            return ("click", far_cell)

        probabilities = self.calculate_probabilities(board)

        best_cell = None
        best_prob = 1.0

        for cell in unknown_cells:
            prob = probabilities.get(cell, 0.5)
            if prob < best_prob:
                best_prob = prob
                best_cell = cell

        if best_cell:
            return ("click", (best_cell[0], best_cell[1]))

        return ("click", random.choice(unknown_cells))


    def _get_unknown_cells(self, board: np.ndarray):
        unknown_mask = (board == -1)
        unknown_positions = np.argwhere(unknown_mask)
        return [(r, c) for r, c in unknown_positions if (r, c) not in self.flagged]

    def _prefer_informative_cell(self, board: np.ndarray, safe_cells: List[Tuple[int, int]]):
        best_cell = safe_cells[0]
        best_score = -1

        for cell in safe_cells:
            score = 0
            neighbours = self.get_neighbours(cell[0], cell[1])

            for nr, nc in neighbours:
                if board[nr, nc] >= 0 and board[nr, nc] <= 8:
                    score += 1
                    if board[nr, nc] == 0:
                        score += 2  # bonus for zeros

            if score > best_score:
                best_score = score
                best_cell = cell

        return best_cell

    def update_flag(self, row: int, col: int, is_flag: bool):
        if is_flag:
            self.flagged.add((row, col))
        else:
            self.flagged.discard((row, col))

    def reset(self):
        self.flagged = set()


def solve_game_browser(board_getter, click_func, flag_func, game_state_func, rows: int, cols: int, mines: int, max_moves: int = 1000):

    solver = MinesweeperSolver(rows, cols, mines)

    first_row = rows // 2
    first_col = cols // 2
    click_func(first_row, first_col)
    time.sleep(0.1)

    board = board_getter()
    moves = 1

    while moves < max_moves:

        game_state_str = game_state_func(board)

        if game_state_str != "playing":
            break

        action = solver.get_action(board, game_state_str)

        if action is None:
            break

        action_type, action_data = action

        if action_type == "click":
            row, col = action_data
            click_func(row, col)
            time.sleep(random.uniform(0.15, 0.4))
            board = board_getter()
            moves += 1
        elif action_type == "flag_all":
            for row, col in action_data:
                flag_func(row, col)
                solver.update_flag(row, col, True)
                board[row, col] = 9
                time.sleep(random.uniform(0.1, 0.2))
            moves += len(action_data)

        if game_state_func(board) != "playing":
            break

    return game_state_func(board) == "won"


def print_board(board: np.ndarray):
    rows, cols = board.shape
    print("\n" + "  " + " ".join(str(i % 10) for i in range(cols)))
    print("  " + "-" * (cols * 2 - 1))
    for r in range(rows):
        row_str = f"{r}|"
        for c in range(cols):
            val = board[r, c]
            if val == -1:
                row_str += " ."
            elif val == 9:
                row_str += " F"
            elif val == 10:
                row_str += " M"
            elif val == 11:
                row_str += " X"
            else:
                row_str += f" {val}"
        print(row_str)
    print()

def solve_game_simulator(rows: int, cols: int, mines: int, max_moves: int = 1000, show_board: bool = False):
    from minesweeper_env import MinesweeperEnv
    env = MinesweeperEnv(rows, cols, mines)
    solver = MinesweeperSolver(rows, cols, mines)
    
    first_row = rows // 2
    first_col = cols // 2
    env.click_cell(first_row, first_col)
    
    if show_board:
        print(f"\nMove 1: Clicked ({first_row}, {first_col})")
        print_board(env.board_state())
    
    moves = 1
    
    while moves < max_moves:
        board = env.board_state()
        game_state_str = env.game_state()
        
        if game_state_str != "playing":
            break
        
        action = solver.get_action(board, game_state_str)
        
        if action is None:
            break
        
        action_type, action_data = action
        
        done = False
        if action_type == "click":
            row, col = action_data
            board, won, done = env.click_cell(row, col)
            moves += 1
            if show_board:
                print(f"Move {moves}: Clicked ({row}, {col})")
                print_board(board)
        elif action_type == "flag_all":
            for row, col in action_data:
                env.flag_cell(row, col)
                solver.update_flag(row, col, True)
            moves += len(action_data)
            board = env.board_state()
            if show_board:
                print(f"Move {moves}: Flagged {len(action_data)} mines")
                print_board(board)
            if show_board:
                print(f"Move {moves}: Flagged ({row}, {col})")
                print_board(board)
            if env.game_state() != "playing":
                done = True
        
        if done:
            if show_board:
                print(f"Game {'WON' if env.won else 'LOST'}!")
            break
    
    return env.game_state() == "won"
