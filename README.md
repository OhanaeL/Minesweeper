# Minesweeper Solver

Automated Minesweeper solver using browser automation/pygame and logical deduction.

> **Note**: This project is primarily for visualization and browser automation purposes. The solver algorithm is not optimized for high win rates or competitive play.

![Demo](assets/minesweeper.gif)

## Installation

```bash
pip install -r requirements.txt
```

For browser automation, choose either Playwright or Selenium:

**Playwright (default):**

```bash
playwright install chromium
```

**Selenium:**

```bash
# ChromeDriver is automatically managed, or install manually:
# Download from https://chromedriver.chromium.org/
```

or

```bash
pip install uv
uv sync
playwright install chromium  # Only needed if using Playwright
```

## Usage

```bash
python main.py
python main.py -m ui
python main.py -m cmd
```

Launches a pygame UI or command prompt that lets you select between:

- Minesweeper via Browser at minesweeper.online or freeminesweeper.org
- Simulated CLI
- Pygame GUI visualization

## Features

- Minesweeper Solver via Logical Deduction
- Browser automation with Playwright or Selenium (choose in menu)
- Simulated environment for testing
- Pygame GUI visualization
- Comprehensive pytest test suite

## Testing

The project includes a comprehensive pytest test suite covering:

- `MinesweeperEnv` - Game environment logic (initialization, cell clicking, flagging, win/loss conditions)
- `MinesweeperSolver` - Solver algorithm (neighbor detection, constraint analysis, probability calculations)
- Game solving functions - End-to-end solver tests

Run tests with:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_minesweeper_env.py

# Run specific test
pytest tests/test_minesweeper_env.py::TestMinesweeperEnv::test_initialization
```

## Mine Solving Process

![Algorithm Flowchart](assets/algorithm.png)

The algorithm works by following these few rules/assumptions:

- If the number of neighbouring flags is equal to the value of a given cell, the rest of the cells must be safe to click on.
- If the number of revealed cells is equal to eight minus the value of the cell, the rest of the cells must be mines.
- If there are no guaranteed cells, get all the neighbouring unrevealed cells and calculate the probability of them being a mine based on their neighbouring revealed cells.
