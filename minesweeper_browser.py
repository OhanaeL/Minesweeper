import time
import re
import numpy as np
from playwright.sync_api import sync_playwright, Page


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
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(config["url"])
    print(f"Website opened: {site}")
    return page, browser, playwright

def main():
    playwright = None
    browser = None

    try:
        page, browser, playwright = open_browser()
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
    finally:
        if browser:
            try:
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
        cells = page.locator(config["cell_selector"]).all()
        max_x = 0
        max_y = 0

        for cell in cells:
            x = int(cell.get_attribute('data-x'))
            y = int(cell.get_attribute('data-y'))
            max_x = max(max_x, x)
            max_y = max(max_y, y)

        width = max_x + 1
        height = max_y + 1
        board = np.full((height, width), -1)

        for cell in cells:
            x = int(cell.get_attribute('data-x'))
            y = int(cell.get_attribute('data-y'))
            cell_class = cell.get_attribute('class') or ''
            matches = re.findall(r'hd_(\w+)', cell_class)
            state = -1
            if matches:
                state = config["cell_state_map"].get(matches[-1], -1)
            board[y, x] = state
            
    elif CURRENT_SITE == "freeminesweeper.org":
        cells = page.locator(config["cell_selector"]).all()
        max_x = 0
        max_y = 0

        for cell in cells:
            name = cell.get_attribute('name')
            match = re.match(r'cellIm(\d+)_(\d+)', name)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        width = max_x + 1
        height = max_y + 1
        board = np.full((height, width), -1)

        for cell in cells:
            name = cell.get_attribute('name')
            match = re.match(r'cellIm(\d+)_(\d+)', name)
            if match:
                x = int(match.group(1))
                y = int(match.group(2))
                img_src = cell.get_attribute('src') or ''
                state = -1
                
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
                    if match_num:
                        state = int(match_num.group(1))
                
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