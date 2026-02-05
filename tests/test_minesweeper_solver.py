import pytest
import numpy as np
from minesweeper_solver import MinesweeperSolver


class TestMinesweeperSolver:
    def test_initialization(self):
        solver = MinesweeperSolver(9, 9, 10)
        assert solver.rows == 9
        assert solver.cols == 9
        assert solver.mines == 10
        assert len(solver.flagged) == 0

    def test_get_neighbours_corner(self):
        solver = MinesweeperSolver(9, 9, 10)
        neighbours = solver.get_neighbours(0, 0)
        assert len(neighbours) == 3
        assert (0, 1) in neighbours
        assert (1, 0) in neighbours
        assert (1, 1) in neighbours

    def test_get_neighbours_edge(self):
        solver = MinesweeperSolver(9, 9, 10)
        neighbours = solver.get_neighbours(0, 4)
        assert len(neighbours) == 5
        assert (0, 3) in neighbours
        assert (0, 5) in neighbours
        assert (1, 3) in neighbours
        assert (1, 4) in neighbours
        assert (1, 5) in neighbours

    def test_get_neighbours_center(self):
        solver = MinesweeperSolver(9, 9, 10)
        neighbours = solver.get_neighbours(4, 4)
        assert len(neighbours) == 8

    def test_get_neighbours_caching(self):
        solver = MinesweeperSolver(9, 9, 10)
        neighbours1 = solver.get_neighbours(4, 4)
        neighbours2 = solver.get_neighbours(4, 4)
        assert neighbours1 is neighbours2

    def test_find_guaranteed_safe_cells(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1]
        ])
        solver.flagged.add((0, 1))
        board[0, 1] = 9
        safe_cells = solver.find_guaranteed_safe_cells(board)
        assert len(safe_cells) > 0
        assert (1, 0) in safe_cells or (1, 1) in safe_cells

    def test_find_guaranteed_mines(self):
        solver = MinesweeperSolver(3, 3, 2)
        board = np.array([
            [2, -1, -1],
            [-1, 0, -1],
            [-1, -1, -1]
        ])
        mine_cells = solver.find_guaranteed_mines(board)
        assert len(mine_cells) == 2
        assert (0, 1) in mine_cells and (1, 0) in mine_cells

    def test_find_guaranteed_safe_all_flagged(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1]
        ])
        solver.flagged.add((0, 1))
        board[0, 1] = 9
        safe_cells = solver.find_guaranteed_safe_cells(board)
        assert len(safe_cells) > 0
        assert (1, 0) in safe_cells or (1, 1) in safe_cells

    def test_find_guaranteed_mines_all_unrevealed(self):
        solver = MinesweeperSolver(3, 3, 2)
        board = np.array([
            [2, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1]
        ])
        board[1, 1] = 0
        mine_cells = solver.find_guaranteed_mines(board)
        assert len(mine_cells) == 2
        assert (0, 1) in mine_cells and (1, 0) in mine_cells

    def test_calculate_probabilities(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1]
        ])
        probabilities = solver.calculate_probabilities(board)
        assert len(probabilities) > 0
        for cell, prob in probabilities.items():
            assert 0 <= prob <= 1

    def test_update_flag(self):
        solver = MinesweeperSolver(9, 9, 10)
        solver.update_flag(0, 0, True)
        assert (0, 0) in solver.flagged
        
        solver.update_flag(0, 0, False)
        assert (0, 0) not in solver.flagged

    def test_reset(self):
        solver = MinesweeperSolver(9, 9, 10)
        solver.update_flag(0, 0, True)
        solver.update_flag(1, 1, True)
        solver.reset()
        assert len(solver.flagged) == 0

    def test_get_action_playing(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1]
        ])
        action = solver.get_action(board, "playing")
        assert action is not None
        assert action[0] in ["click", "flag_all"]

    def test_get_action_won(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ])
        action = solver.get_action(board, "won")
        assert action is None

    def test_get_action_lost(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, 1, 1],
            [1, 11, 1],
            [1, 1, 1]
        ])
        action = solver.get_action(board, "lost")
        assert action is None

    def test_get_unknown_cells(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ])
        solver.flagged.add((1, 1))
        unknown = solver._get_unknown_cells(board)
        assert (1, 1) not in unknown
        assert len(unknown) == 7

    def test_prefer_informative_cell(self):
        solver = MinesweeperSolver(5, 5, 1)
        board = np.array([
            [0, 1, -1, -1, -1],
            [1, 2, -1, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1]
        ])
        safe_cells = [(2, 0), (0, 2), (2, 2)]
        best = solver._prefer_informative_cell(board, safe_cells)
        assert best in safe_cells

    def test_is_early_game(self):
        solver = MinesweeperSolver(9, 9, 10)
        board = np.full((9, 9), -1)
        assert solver._is_early_game(board) == True
        
        board[4, 4] = 1
        assert solver._is_early_game(board) == True
        
        board[0, 0] = 0
        assert solver._is_early_game(board) == False
        
        board = np.full((9, 9), -1)
        for i in range(10):
            board[i // 9, i % 9] = 1
        assert solver._is_early_game(board) == False

    def test_get_cell_far_from_revealed(self):
        solver = MinesweeperSolver(9, 9, 10)
        board = np.full((9, 9), -1)
        board[4, 4] = 1
        unknown = solver._get_unknown_cells(board)
        far_cell = solver._get_cell_far_from_revealed(board, unknown)
        assert far_cell in unknown

    def test_get_cell_far_from_revealed_no_revealed(self):
        solver = MinesweeperSolver(9, 9, 10)
        board = np.full((9, 9), -1)
        unknown = solver._get_unknown_cells(board)
        far_cell = solver._get_cell_far_from_revealed(board, unknown)
        assert far_cell in unknown

    def test_action_flag_all(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [2, -1, -1],
            [-1, -1, -1],
            [-1, -1, -1]
        ])
        action = solver.get_action(board, "playing")
        assert action is not None
        if action[0] == "flag_all":
            assert len(action[1]) == 2

    def test_action_click_safe(self):
        solver = MinesweeperSolver(3, 3, 1)
        board = np.array([
            [1, 1, 1],
            [1, -1, -1],
            [-1, -1, -1]
        ])
        solver.flagged.add((0, 0))
        board[0, 0] = 9
        action = solver.get_action(board, "playing")
        assert action is not None
        assert action[0] == "click"
        assert action[1] in [(0, 2), (1, 1), (2, 0), (2, 1)]
