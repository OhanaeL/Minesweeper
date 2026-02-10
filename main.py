import random
import time
import argparse

from menu_ui import MenuGUI
from minesweeper_ui import MinesweeperGUI
from minesweeper_browser import open_browser as open_browser_playwright, board_state as board_state_playwright, click_cell as click_cell_playwright, flag_cell as flag_cell_playwright, game_state, start_game as start_game_playwright, restart_game as restart_game_playwright
from minesweeper_browser_selenium import open_browser as open_browser_selenium, board_state as board_state_selenium, click_cell as click_cell_selenium, flag_cell as flag_cell_selenium, start_game as start_game_selenium, restart_game as restart_game_selenium
from minesweeper_solver import solve_game_browser, solve_game_simulator

import minesweeper_browser
import minesweeper_browser_selenium


def run_browser_mode(site, difficulty, num_games, browser_lib="playwright"):
    if site == "freeminesweeper.org":
        difficulty = "intermediate"

    print(f"\nTesting solver on browser ({site}, {difficulty} difficulty, {num_games} games, {browser_lib})...")

    if browser_lib == "selenium":
        minesweeper_browser_selenium.CURRENT_SITE = site
        driver = open_browser_selenium(site)
        
        try:
            wins = 0

            for game_num in range(1, num_games + 1):
                print(f"\nGame {game_num}/{num_games}")

                if game_num > 1:
                    restart_game_selenium(driver, difficulty)
                else:
                    start_game_selenium(driver, difficulty)

                board = board_state_selenium(driver)
                rows, cols = board.shape

                difficulty_mines = {
                    "easy": 10,
                    "intermediate": 40,
                    "expert": 99
                }
                mines = difficulty_mines.get(difficulty, 10)

                won = solve_game_browser(
                    board_getter=lambda: board_state_selenium(driver),
                    click_func=lambda r, c: click_cell_selenium(driver, c, r),
                    flag_func=lambda r, c: flag_cell_selenium(driver, c, r),
                    game_state_func=lambda b: game_state(b),
                    rows=rows,
                    cols=cols,
                    mines=mines
                )

                if won:
                    wins += 1
                    print(f"Won!")
                else:
                    print(f"Lost")

                win_rate = (wins / game_num) * 100
                print(f"Win Rate: {win_rate:.1f}%")

                if game_num < num_games:
                    time.sleep(random.uniform(1.0, 3.0))

            print(f"\n{'='*50}")
            print(f"Final Results:")
            print(f"Games Played: {num_games}")
            print(f"Wins: {wins}")
            print(f"Win Rate: {(wins/num_games)*100:.1f}%")
            print(f"{'='*50}")

        except Exception as e:
            print(f"Error during game execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\nClosing browser in 3 seconds... (Press Ctrl+C to keep it open)")
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                print("\nBrowser kept open. Close it manually when done.")
                input("Press Enter to close the browser: ")
            driver.quit()
    else:
        minesweeper_browser.CURRENT_SITE = site
        page, browser, playwright = open_browser_playwright(site)

        try:
            wins = 0

            for game_num in range(1, num_games + 1):
                print(f"\nGame {game_num}/{num_games}")

                if game_num > 1:
                    restart_game_playwright(page, difficulty)
                else:
                    start_game_playwright(page, difficulty)

                board = board_state_playwright(page)
                rows, cols = board.shape

                difficulty_mines = {
                    "easy": 10,
                    "intermediate": 40,
                    "expert": 99
                }
                mines = difficulty_mines.get(difficulty, 10)

                won = solve_game_browser(
                    board_getter=lambda: board_state_playwright(page),
                    click_func=lambda r, c: click_cell_playwright(page, c, r),
                    flag_func=lambda r, c: flag_cell_playwright(page, c, r),
                    game_state_func=lambda b: game_state(b),
                    rows=rows,
                    cols=cols,
                    mines=mines
                )

                if won:
                    wins += 1
                    print(f"Won!")
                else:
                    print(f"Lost")

                win_rate = (wins / game_num) * 100
                print(f"Win Rate: {win_rate:.1f}%")

                if game_num < num_games:
                    time.sleep(random.uniform(1.0, 3.0))

            print(f"\n{'='*50}")
            print(f"Final Results:")
            print(f"Games Played: {num_games}")
            print(f"Wins: {wins}")
            print(f"Win Rate: {(wins/num_games)*100:.1f}%")
            print(f"{'='*50}")

        except Exception as e:
            print(f"Error during game execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\nClosing browser in 3 seconds... (Press Ctrl+C to keep it open)")
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                print("\nBrowser kept open. Close it manually when done.")
                input("Press Enter to close the browser: ")
            browser.close()
            playwright.stop()


def run_simulated_mode(difficulty, num_games, show_board):
    difficulty_configs = {
        "easy": (9, 9, 10),
        "intermediate": (16, 16, 40),
        "expert": (16, 30, 99),
    }

    rows, cols, mines = difficulty_configs[difficulty]

    print(f"\nTesting solver on simulated environment ({difficulty}, {rows}x{cols}, {mines} mines, {num_games} games)...")

    wins = 0
    total_time = 0

    for game_num in range(1, num_games + 1):
        if not show_board:
            print(f"\nGame {game_num}/{num_games}", end="", flush=True)

        start_time = time.time()
        won = solve_game_simulator(rows, cols, mines, show_board=show_board)
        elapsed = time.time() - start_time

        if won:
            wins += 1
            if not show_board:
                print(" - Won", end="", flush=True)
        else:
            if not show_board:
                print(" - Lost", end="", flush=True)

        total_time += elapsed

        if not show_board and game_num % 10 == 0:
            win_rate = (wins / game_num) * 100
            avg_time = total_time / game_num
            print(f"\n  Progress: {game_num} games, {wins} wins ({win_rate:.1f}%), Avg: {avg_time*1000:.1f}ms")
        elif show_board:
            print(f"\nGame {game_num}/{num_games}: {'Won' if won else 'Lost'}")
            print("-" * 50)

    final_win_rate = (wins / num_games) * 100
    avg_time = total_time / num_games

    print(f"\n{'='*50}")
    print(f"Final Results:")
    print(f"Games Played: {num_games}")
    print(f"Wins: {wins}")
    print(f"Win Rate: {final_win_rate:.1f}%")
    print(f"Average Time: {avg_time*1000:.1f}ms per game")
    print(f"{'='*50}")


def run_ui_mode(difficulty="intermediate"):
    difficulty_configs = {
        "easy": (9, 9, 10),
        "intermediate": (16, 16, 40),
        "expert": (16, 30, 99),
    }

    rows, cols, mines = difficulty_configs[difficulty]


    print(f"\nLaunching GUI ({difficulty}, {rows}x{cols}, {mines} mines)...")
    print("Click 'Start Solving' to begin!")

    gui = MinesweeperGUI(rows, cols, mines)
    gui.run()


def run_cmd_mode():
    print("Minesweeper Solver")
    print("=" * 50)

    mode = input("Run in browser, simulated, or ui? (browser/simulated/ui): ").strip().lower()

    if mode == "browser":
        site = input("Which website? (minesweeper.online/freeminesweeper.org): ").strip().lower()

        if site not in ["minesweeper.online", "freeminesweeper.org"]:
            print("Invalid site. Using minesweeper.online")
            site = "minesweeper.online"

        difficulty = "intermediate"
        if site == "minesweeper.online":
            difficulty = input("Difficulty? (easy/intermediate/expert): ").strip().lower()
            if difficulty not in ["easy", "intermediate", "expert"]:
                print("Invalid difficulty. Using intermediate")
                difficulty = "intermediate"
        elif site == "freeminesweeper.org":
            print("Note: freeminesweeper.org only supports intermediate difficulty")
            difficulty = "intermediate"

        num_games = int(input("How many games? ").strip() or "10")
        browser_lib = input("Browser library? (playwright/selenium): ").strip().lower() or "playwright"
        if browser_lib not in ["playwright", "selenium"]:
            print("Invalid browser library. Using playwright")
            browser_lib = "playwright"
        run_browser_mode(site, difficulty, num_games, browser_lib)

    elif mode == "simulated":
        difficulty = input("Difficulty? (easy/intermediate/expert): ").strip().lower()

        if difficulty not in ["easy", "intermediate", "expert"]:
            print("Invalid difficulty. Using intermediate")
            difficulty = "intermediate"

        num_games = int(input("How many games? ").strip() or "100")
        show_board = input("Show board state? (y/n): ").strip().lower() == "y"
        run_simulated_mode(difficulty, num_games, show_board)

    elif mode == "ui":
        difficulty = input("Difficulty? (easy/intermediate/expert): ").strip().lower()

        if difficulty not in ["easy", "intermediate", "expert"]:
            print("Invalid difficulty. Using intermediate")
            difficulty = "intermediate"

        run_ui_mode(difficulty)

    else:
        print("Invalid mode. Please choose 'browser', 'simulated', or 'ui'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Minesweeper Solver')
    parser.add_argument('-m', '--mode', dest='mode', choices=['ui', 'cmd'], help='Mode: ui (default GUI menu), cmd (command-line interface)')
    args = parser.parse_args()

    if args.mode == 'ui':
        # direct ui mode - skip menu and launch UI with default settings
        run_ui_mode()
    elif args.mode == 'cmd':
        # command line mode
        run_cmd_mode()
    else:
        # default: show menu GUI
        menu = MenuGUI()
        config = menu.run()

        if config is None:
            exit(0)

        mode = config['mode']
        site = config.get('site', 'minesweeper.online')
        browser_lib = config.get('browser_lib', 'playwright')
        difficulty = config['difficulty']
        num_games = config['num_games']
        show_board = config.get('show_board', False)

        if mode == "browser":
            run_browser_mode(site, difficulty, num_games, browser_lib)
        elif mode == "simulated":
            run_simulated_mode(difficulty, num_games, show_board)
        elif mode == "ui":
            run_ui_mode(difficulty)

