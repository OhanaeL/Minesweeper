import time
import re
import numpy as np
from playwright.sync_api import sync_playwright, Page
import subprocess
import sys


# Ensure Playwright browsers are installed
def ensure_playwright_browsers():
    try:
        sync_playwright().start().stop()
    except Exception:
        print("Playwright browsers not found. Installing...")
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
        print("Playwright browsers installed successfully!")

ensure_playwright_browsers()


SITE_CONFIGS = {
    "minesweeper.online": {
        "url": "https://minesweeper.online/",
        "difficulty_classes": {
            "easy": ".homepage-level-1",
            "intermediate": ".homepage-level-2",
            "expert": ".homepage-level-3",
        },
        "difficulty_ids": {
            "easy": "#level_select_1",
            "intermediate": "#level_select_2",
            "expert": "#level_select_3",
        },
        "cell_selector": "#AreaBlock .cell",
        "cell_state_map": {
            "type0": 0, "type1": 1, "type2": 2, "type3": 3, "type4": 4,
            "type5": 5, "type6": 6, "type7": 7, "type8": 8,
            "type10": 10, "type11": 11, "type12": 12,
            "closed": -1, "flag": 9,
        },
    },
    "freeminesweeper.org": {
        "url": "https://freeminesweeper.org/",
        "difficulty_classes": {},
        "difficulty_ids": {},
        "cell_selector": "img[name^='cellIm']",
        "cell_state_map": {
            "open0": 0, "open1": 1, "open2": 2, "open3": 3, "open4": 4,
            "open5": 5, "open6": 6, "open7": 7, "open8": 8,
            "blank": -1, "flag": 9, "mine": 10, "exploded": 11,
        },
    },
}

CURRENT_SITE = "minesweeper.online"

AD_SELECTORS = [
    ".adsbygoogle",
    ".adsbygoogle-noablate",
    "[id^='aswift']"
]


def game_state(board):
    if np.any(board == 11):
        return "lost"
    if np.all(board != -1):
        return "won"
    return "playing"

def element_exists(page: Page, selectors: str | list[str]) -> bool:
    if isinstance(selectors, str):
        selectors = [selectors]
    for selector in selectors:
        if page.locator(selector).count() > 0:
            return True
    return False

def handle_ads(page: Page) -> None:
    if CURRENT_SITE == "minesweeper.online":
        if element_exists(page, AD_SELECTORS):
            close_ad(page)
            print("Ads closed")
        else:
            print("No ads found")
    elif CURRENT_SITE == "freeminesweeper.org":
        pass

def close_ad(page: Page) -> None:
    time.sleep(0.5)

    js_selectors = str(AD_SELECTORS)

    page.evaluate(f"""
        () => {{
            const selectors = {js_selectors};
            selectors.forEach(selector => {{
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => element.remove());
            }});
        }}
    """)

    time.sleep(0.3)

def open_browser(site="minesweeper.online"):
    global CURRENT_SITE
    CURRENT_SITE = site
    config = SITE_CONFIGS[site]
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.new_page()
    page.goto(config["url"])
    print(f"Website opened: {site}")
    return page, browser, playwright

def main():
    playwright = None
    browser = None

    try:
        page, browser, playwright = open_browser()
        print("Browser is open. Keep this window open to see the solver in action.")
        time.sleep(1)  # Give browser time to fully load
        
        difficulty = input("Enter difficulty (easy, intermediate, expert): ")
        start_game(page, difficulty)

        while True:
            board = board_state(page)
            print(board)
            close = input("Enter 'close' to close the browser: ")
            if close == "close":
                break

    except KeyboardInterrupt:
        print("\n\nClosing browser...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if browser:
            try:
                print("Closing browser...")
                browser.close()
            except:
                pass
        if playwright:
            try:
                playwright.stop()
            except:
                pass

def undo_button(page):
    page.click("#restart_btn")
    time.sleep(2)
    print("Undo button clicked")

def start_game(page, difficulty="intermediate"):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        page.click(config["difficulty_classes"][difficulty])
        handle_ads(page)
        print("Game started!")
    elif CURRENT_SITE == "freeminesweeper.org":
        print("Game already started!")

def restart_game(page, difficulty="intermediate"):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        page.click(config["difficulty_ids"][difficulty])
        handle_ads(page)
    elif CURRENT_SITE == "freeminesweeper.org":
        page.reload()
        time.sleep(1)
    print("Game restarted!")

def board_state(page):
    config = SITE_CONFIGS[CURRENT_SITE]
    
    if CURRENT_SITE == "minesweeper.online":
        board_data = page.evaluate("""
            () => {
                const cells = document.querySelectorAll('#AreaBlock .cell');
                const board = {};
                let max_x = 0, max_y = 0;
                
                cells.forEach(cell => {
                    const x = parseInt(cell.dataset.x);
                    const y = parseInt(cell.dataset.y);
                    max_x = Math.max(max_x, x);
                    max_y = Math.max(max_y, y);
                    
                    const classList = Array.from(cell.classList);
                    const typeMatch = classList.find(c => c.startsWith('hd_'));
                    const type = typeMatch ? typeMatch.replace('hd_', '') : 'closed';
                    
                    board[`${x},${y}`] = type;
                });
                
                return { board, width: max_x + 1, height: max_y + 1 };
            }
        """)
        
        width = board_data['width']
        height = board_data['height']
        board = np.full((height, width), -1)
        
        state_map = config["cell_state_map"]
        for key, state_str in board_data['board'].items():
            x, y = map(int, key.split(','))
            board[y, x] = state_map.get(state_str, -1)
        
        return board
    
    elif CURRENT_SITE == "freeminesweeper.org":
        board_data = page.evaluate("""
            () => {
                const cells = document.querySelectorAll('img[name^="cellIm"]');
                const board = {};
                let max_x = 0, max_y = 0;
                
                cells.forEach(cell => {
                    const match = cell.name.match(/cellIm(\\d+)_(\\d+)/);
                    if (match) {
                        const x = parseInt(match[1]);
                        const y = parseInt(match[2]);
                        max_x = Math.max(max_x, x);
                        max_y = Math.max(max_y, y);
                        board[`${x},${y}`] = cell.src;
                    }
                });
                
                return { board, width: max_x + 1, height: max_y + 1 };
            }
        """)
        
        width = board_data['width']
        height = board_data['height']
        board = np.full((height, width), -1)
        
        for key, img_src in board_data['board'].items():
            x, y = map(int, key.split(','))
            if 'blank.gif' in img_src:
                state = -1
            elif 'flag' in img_src.lower():
                state = 9
            elif 'bombdeath' in img_src.lower():
                state = 11
            elif 'bombrevealed' in img_src.lower():
                state = 10
            else:
                match_num = re.search(r'open(\d+)', img_src)
                state = int(match_num.group(1)) if match_num else -1
            
            board[y, x] = state
        
        return board

def click_cell(page, x, y):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        page.click(f'#cell_{x}_{y}')
    elif CURRENT_SITE == "freeminesweeper.org":
        anchor = page.locator(f'a:has(img[name="cellIm{x}_{y}"])')
        anchor.click()
    print(f"Clicked cell {x}, {y}")
    time.sleep(0.1)

def flag_cell(page, x, y):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        page.locator(f'#cell_{x}_{y}').click(button='right')
    elif CURRENT_SITE == "freeminesweeper.org":
        anchor = page.locator(f'a:has(img[name="cellIm{x}_{y}"])')
        anchor.click(button='right')
    print(f"Flagged cell {x}, {y}")
    time.sleep(0.1)

if __name__ == "__main__":
    main()