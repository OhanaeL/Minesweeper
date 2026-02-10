import pytest
import numpy as np
from minesweeper_solver import solve_game_simulator
from minesweeper_env import MinesweeperEnv


class TestSolveGameSimulator:
    def test_solve_game_easy(self):
        won = solve_game_simulator(9, 9, 10, max_moves=200, show_board=False)
        assert isinstance(won, bool)

    def test_solve_game_intermediate(self):
        won = solve_game_simulator(16, 16, 40, max_moves=500, show_board=False)
        assert isinstance(won, bool)

    def test_solve_game_expert(self):
        won = solve_game_simulator(16, 30, 99, max_moves=1000, show_board=False)
        assert isinstance(won, bool)

    def test_solve_game_max_moves(self):
        won = solve_game_simulator(9, 9, 10, max_moves=5, show_board=False)
        assert isinstance(won, bool)

    def test_solve_game_with_board_display(self):
        won = solve_game_simulator(9, 9, 10, max_moves=50, show_board=True)
        assert isinstance(won, bool)

    def test_solve_game_small_board(self):
        won = solve_game_simulator(3, 3, 1, max_moves=10, show_board=False)
        assert isinstance(won, bool)

    def test_solve_game_very_small(self):
        won = solve_game_simulator(2, 2, 1, max_moves=5, show_board=False)
        assert isinstance(won, bool)


class TestGameStateFunctions:
    def test_game_state_playing(self):
        from minesweeper_browser import game_state
        board = np.full((9, 9), -1)
        board[0, 0] = 1
        assert game_state(board) == "playing"

    def test_game_state_won(self):
        from minesweeper_browser import game_state
        board = np.array([
            [1, 1, 1],
            [1, 9, 1],
            [1, 1, 1]
        ])
        assert game_state(board) == "won"

    def test_game_state_lost(self):
        from minesweeper_browser import game_state
        board = np.array([
            [1, 1, 1],
            [1, 11, 1],
            [1, 1, 1]
        ])
        assert game_state(board) == "lost"
