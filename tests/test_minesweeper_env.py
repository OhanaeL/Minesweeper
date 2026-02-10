import pytest
import numpy as np
from minesweeper_env import MinesweeperEnv


class TestMinesweeperEnv:
    def test_initialization(self):
        env = MinesweeperEnv(9, 9, 10)
        assert env.rows == 9
        assert env.cols == 9
        assert env.mines == 10
        assert env.game_over == False
        assert env.won == False
        assert np.all(env.board == -1)
        assert np.sum(env.revealed) == 0
        assert np.sum(env.flagged) == 0

    def test_reset(self):
        env = MinesweeperEnv(9, 9, 10)
        env.click_cell(0, 0)
        env.reset()
        assert env.game_over == False
        assert env.won == False
        assert np.all(env.board == -1)
        assert len(env.mine_positions) == 0

    def test_first_click_safe(self):
        env = MinesweeperEnv(9, 9, 10)
        board, won, done = env.click_cell(4, 4)
        assert not done
        assert not won
        assert board[4, 4] != -1
        assert (4, 4) not in env.mine_positions
        for r in range(max(0, 4-1), min(9, 4+2)):
            for c in range(max(0, 4-1), min(9, 4+2)):
                assert (r, c) not in env.mine_positions

    def test_click_mine(self):
        env = MinesweeperEnv(3, 3, 8)
        env._place_mines(0, 0)
        mine_pos = list(env.mine_positions)[0]
        board, won, done = env.click_cell(mine_pos[0], mine_pos[1])
        assert done
        assert not won
        assert board[mine_pos[0], mine_pos[1]] == 11
        assert env.exploded_mine == mine_pos

    def test_flag_cell(self):
        env = MinesweeperEnv(9, 9, 10)
        env.flag_cell(0, 0)
        assert env.board[0, 0] == 9
        assert env.flagged[0, 0] == True
        
        env.flag_cell(0, 0)
        assert env.board[0, 0] == -1
        assert env.flagged[0, 0] == False

    def test_flag_revealed_cell(self):
        env = MinesweeperEnv(9, 9, 10)
        env.click_cell(4, 4)
        initial_state = env.board[4, 4].copy()
        env.flag_cell(4, 4)
        assert env.board[4, 4] == initial_state
        assert env.flagged[4, 4] == False

    def test_click_flagged_cell(self):
        env = MinesweeperEnv(9, 9, 10)
        env.flag_cell(0, 0)
        board, won, done = env.click_cell(0, 0)
        assert env.board[0, 0] == 9
        assert not done

    def test_win_condition(self):
        env = MinesweeperEnv(3, 3, 1)
        env._place_mines(0, 0)
        mine_pos = list(env.mine_positions)[0]
        
        for r in range(3):
            for c in range(3):
                if (r, c) != mine_pos:
                    env.click_cell(r, c)
        
        assert env.game_over
        assert env.won
        assert env.game_state() == "won"

    def test_reveal_remaining_mines_on_win(self):
        env = MinesweeperEnv(3, 3, 1)
        env._place_mines(0, 0)
        mine_pos = list(env.mine_positions)[0]
        
        for r in range(3):
            for c in range(3):
                if (r, c) != mine_pos:
                    env.click_cell(r, c)
        
        env.reveal_remaining_mines()
        assert env.board[mine_pos[0], mine_pos[1]] == 9

    def test_reveal_all_mines_on_loss(self):
        env = MinesweeperEnv(3, 3, 2)
        env._place_mines(0, 0)
        mine_positions = list(env.mine_positions)
        env.click_cell(mine_positions[0][0], mine_positions[0][1])
        
        env.reveal_all_mines()
        for mine_pos in mine_positions:
            if mine_pos == env.exploded_mine:
                assert env.board[mine_pos[0], mine_pos[1]] == 11
            else:
                assert env.board[mine_pos[0], mine_pos[1]] == 10

    def test_game_state_playing(self):
        env = MinesweeperEnv(9, 9, 10)
        assert env.game_state() == "playing"
        env.click_cell(4, 4)
        assert env.game_state() == "playing"

    def test_game_state_lost(self):
        env = MinesweeperEnv(3, 3, 8)
        env._place_mines(0, 0)
        mine_pos = list(env.mine_positions)[0]
        env.click_cell(mine_pos[0], mine_pos[1])
        assert env.game_state() == "lost"

    def test_game_state_won(self):
        env = MinesweeperEnv(3, 3, 1)
        env._place_mines(0, 0)
        mine_pos = list(env.mine_positions)[0]
        
        for r in range(3):
            for c in range(3):
                if (r, c) != mine_pos:
                    env.click_cell(r, c)
        
        assert env.game_state() == "won"

    def test_zero_cell_auto_reveal(self):
        env = MinesweeperEnv(5, 5, 1)
        env._place_mines(0, 0)
        mine_pos = list(env.mine_positions)[0]
        
        zero_cell = None
        for r in range(5):
            for c in range(5):
                if (r, c) != mine_pos:
                    count = 0
                    for nr in range(max(0, r-1), min(5, r+2)):
                        for nc in range(max(0, c-1), min(5, c+2)):
                            if (nr, nc) in env.mine_positions:
                                count += 1
                    if count == 0:
                        zero_cell = (r, c)
                        break
            if zero_cell:
                break
        
        if zero_cell:
            board, _, _ = env.click_cell(zero_cell[0], zero_cell[1])
            assert board[zero_cell[0], zero_cell[1]] == 0
            revealed_count = np.sum(env.revealed)
            assert revealed_count > 1

    def test_board_state_copy(self):
        env = MinesweeperEnv(9, 9, 10)
        env.click_cell(4, 4)
        board1 = env.board_state()
        board2 = env.board_state()
        assert np.array_equal(board1, board2)
        board1[0, 0] = 99
        assert env.board[0, 0] != 99

    def test_click_after_game_over(self):
        env = MinesweeperEnv(3, 3, 8)
        env._place_mines(0, 0)
        mine_pos = list(env.mine_positions)[0]
        env.click_cell(mine_pos[0], mine_pos[1])
        
        board, won, done = env.click_cell(0, 0)
        assert done
        assert not won
