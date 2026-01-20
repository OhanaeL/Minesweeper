import time
import re
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


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

def element_exists(driver, selectors):
    if isinstance(selectors, str):
        selectors = [selectors]
    for selector in selectors:
        if len(driver.find_elements(By.CSS_SELECTOR, selector)) > 0:
            return True
    return False

def handle_ads(driver):
    if CURRENT_SITE == "minesweeper.online":
        if element_exists(driver, AD_SELECTORS):
            close_ad(driver)
            print("Ads closed")
        else:
            print("No ads found")
    elif CURRENT_SITE == "freeminesweeper.org":
        pass

def close_ad(driver):
    time.sleep(0.5)

    js_selectors = str(AD_SELECTORS)

    driver.execute_script(f"""
        const selectors = {js_selectors};
        selectors.forEach(selector => {{
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => element.remove());
        }});
    """)

    time.sleep(0.3)

def open_browser(site="minesweeper.online"):
    global CURRENT_SITE
    CURRENT_SITE = site
    config = SITE_CONFIGS[site]
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(config["url"])
    print(f"Website opened: {site}")
    return driver

def main():
    driver = None

    try:
        driver = open_browser()
        difficulty = input("Enter difficulty (easy, intermediate, expert): ")
        start_game(driver, difficulty)

        while True:
            board = board_state(driver)
            print(board)
            close = input("Enter 'close' to close the browser: ")
            if close == "close":
                break

    except KeyboardInterrupt:
        print("\n\nClosing browser...")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def undo_button(driver):
    driver.find_element(By.CSS_SELECTOR, "#restart_btn").click()
    time.sleep(2)
    print("Undo button clicked")

def start_game(driver, difficulty="intermediate"):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        driver.find_element(By.CSS_SELECTOR, config["difficulty_classes"][difficulty]).click()
        handle_ads(driver)
        print("Game started!")
    elif CURRENT_SITE == "freeminesweeper.org":
        print("Game already started!")

def restart_game(driver, difficulty="intermediate"):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        driver.find_element(By.CSS_SELECTOR, config["difficulty_ids"][difficulty]).click()
        handle_ads(driver)
    elif CURRENT_SITE == "freeminesweeper.org":
        driver.refresh()
        time.sleep(1)
    print("Game restarted!")

def board_state(driver):
    config = SITE_CONFIGS[CURRENT_SITE]
    
    if CURRENT_SITE == "minesweeper.online":
        cells = driver.find_elements(By.CSS_SELECTOR, config["cell_selector"])
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
        cells = driver.find_elements(By.CSS_SELECTOR, config["cell_selector"])
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

def click_cell(driver, x, y):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        driver.find_element(By.CSS_SELECTOR, f'#cell_{x}_{y}').click()
    elif CURRENT_SITE == "freeminesweeper.org":
        img = driver.find_element(By.CSS_SELECTOR, f'img[name="cellIm{x}_{y}"]')
        anchor = img.find_element(By.XPATH, './parent::a')
        anchor.click()
    print(f"Clicked cell {x}, {y}")
    time.sleep(0.1)

def flag_cell(driver, x, y):
    config = SITE_CONFIGS[CURRENT_SITE]
    if CURRENT_SITE == "minesweeper.online":
        element = driver.find_element(By.CSS_SELECTOR, f'#cell_{x}_{y}')
        ActionChains(driver).context_click(element).perform()
    elif CURRENT_SITE == "freeminesweeper.org":
        img = driver.find_element(By.CSS_SELECTOR, f'img[name="cellIm{x}_{y}"]')
        anchor = img.find_element(By.XPATH, './parent::a')
        ActionChains(driver).context_click(anchor).perform()
    print(f"Flagged cell {x}, {y}")
    time.sleep(0.1)

if __name__ == "__main__":
    main()
