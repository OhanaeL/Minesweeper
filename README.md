# Minesweeper Solver

Automated Minesweeper solver using browser automation/pygame and logical deduction.

![Demo](assets/minesweeper.gif)

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

or

```bash
pip install uv
uv sync
playwright install chromium
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
- Browser automation with Playwright
- Simulated environment for testing
- Pygame GUI visualization

## Logical Detection Process

![Algorithm Flowchart](assets/algorithm.png)
