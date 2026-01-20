import pygame
import os


class MenuGUI:
    def __init__(self):
        pygame.init()
        self.width = 600
        self.height = 500
        
        # Ensure button is visible - adjust if needed
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper Solver - Menu")
        self.clock = pygame.time.Clock()
        
        font_path = os.path.join("assets", "font", "upheaval", "upheavtt.ttf")
        try:
            self.title_font = pygame.font.Font(font_path, 36)
            self.font = pygame.font.Font(font_path, 24)
            self.small_font = pygame.font.Font(font_path, 20)
            self.option_font = pygame.font.Font(font_path, 18)
        except:
            try:
                self.title_font = pygame.font.Font(pygame.font.get_default_font(), 36)
                self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
                self.small_font = pygame.font.Font(pygame.font.get_default_font(), 20)
                self.option_font = pygame.font.Font(pygame.font.get_default_font(), 18)
            except:
                self.title_font = pygame.font.Font(None, 36)
                self.font = pygame.font.Font(None, 24)
                self.small_font = pygame.font.Font(None, 20)
                self.option_font = pygame.font.Font(None, 18)
        
        self.colors = {
            'bg': (240, 240, 240),
            'text': (30, 30, 30),
            'button': (70, 130, 180),
            'button_hover': (100, 160, 210),
            'button_active': (50, 100, 150),
            'dropdown': (255, 255, 255),
            'dropdown_border': (150, 150, 150),
            'dropdown_hover': (240, 240, 240),
        }
        
        # Menu state
        self.mode = "ui"
        self.site = "minesweeper.online"
        self.browser_lib = "playwright"
        self.difficulty = "intermediate"
        self.num_games = "1"
        self.show_board = False
        
        # Dropdown states
        self.mode_dropdown_open = False
        self.site_dropdown_open = False
        self.browser_lib_dropdown_open = False
        self.difficulty_dropdown_open = False
        
        # Rectangles
        self.mode_rect = pygame.Rect(50, 120, 250, 40)
        self.site_rect = pygame.Rect(320, 120, 250, 40)
        self.browser_lib_rect = pygame.Rect(50, 200, 250, 40)
        self.difficulty_rect = pygame.Rect(320, 200, 250, 40)
        self.num_games_rect = pygame.Rect(50, 280, 250, 40)
        self.show_board_rect = pygame.Rect(320, 280, 250, 40)
        self.start_button_rect = pygame.Rect(50, 350, 500, 80)
        
        self.mode_options = ["ui", "browser", "simulated"]
        self.site_options = ["minesweeper.online", "freeminesweeper.org"]
        self.browser_lib_options = ["playwright", "selenium"]
        self.difficulty_options = ["easy", "intermediate", "expert"]
        
        self.selected = None
        self.running = True
        
    def draw_dropdown(self, rect, text, options, is_open, selected_value):
        # Draw dropdown box
        color = self.colors['dropdown_hover'] if rect.collidepoint(pygame.mouse.get_pos()) else self.colors['dropdown']
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], rect, 2)
        
        # Draw selected text
        text_surface = self.font.render(str(selected_value), True, self.colors['text'])
        text_x = rect.x + 10
        text_y = rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Draw arrow
        arrow_size = 8
        arrow_x = rect.right - 20
        arrow_y = rect.centery
        if is_open:
            pygame.draw.polygon(self.screen, self.colors['text'], 
                              [(arrow_x, arrow_y - arrow_size//2),
                               (arrow_x + arrow_size, arrow_y - arrow_size//2),
                               (arrow_x + arrow_size//2, arrow_y + arrow_size//2)])
        else:
            pygame.draw.polygon(self.screen, self.colors['text'],
                              [(arrow_x, arrow_y + arrow_size//2),
                               (arrow_x + arrow_size, arrow_y + arrow_size//2),
                               (arrow_x + arrow_size//2, arrow_y - arrow_size//2)])
        
        # Draw dropdown options if open
        if is_open:
            dropdown_height = len(options) * 35
            dropdown_rect = pygame.Rect(rect.x, rect.bottom, rect.width, dropdown_height)
            pygame.draw.rect(self.screen, self.colors['dropdown'], dropdown_rect)
            pygame.draw.rect(self.screen, self.colors['dropdown_border'], dropdown_rect, 2)
            
            for i, option in enumerate(options):
                option_rect = pygame.Rect(rect.x, rect.bottom + i * 35, rect.width, 35)
                mouse_pos = pygame.mouse.get_pos()
                if option_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, self.colors['dropdown_hover'], option_rect)
                
                option_text = self.font.render(str(option), True, self.colors['text'])
                option_y = option_rect.centery - option_text.get_height() // 2
                self.screen.blit(option_text, (option_rect.x + 10, option_y))
    
    def draw_text_input(self, rect, text, label):
        # Draw label
        label_surface = self.small_font.render(label, True, self.colors['text'])
        self.screen.blit(label_surface, (rect.x, rect.y - 25))
        
        # Draw input box
        color = self.colors['dropdown_hover'] if rect.collidepoint(pygame.mouse.get_pos()) else self.colors['dropdown']
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], rect, 2)
        
        # Draw text
        text_surface = self.font.render(str(text), True, self.colors['text'])
        text_x = rect.x + 10
        text_y = rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_checkbox(self, rect, checked, label):
        # Draw label
        label_surface = self.small_font.render(label, True, self.colors['text'])
        self.screen.blit(label_surface, (rect.x, rect.y - 25))
        
        # Draw checkbox
        checkbox_size = 30
        checkbox_rect = pygame.Rect(rect.x, rect.y, checkbox_size, checkbox_size)
        pygame.draw.rect(self.screen, self.colors['dropdown'], checkbox_rect)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], checkbox_rect, 2)
        
        if checked:
            check_size = 20
            pygame.draw.line(self.screen, (0, 150, 0), 
                           (checkbox_rect.x + 5, checkbox_rect.centery),
                           (checkbox_rect.x + check_size//2, checkbox_rect.bottom - 5), 3)
            pygame.draw.line(self.screen, (0, 150, 0),
                           (checkbox_rect.x + check_size//2, checkbox_rect.bottom - 5),
                           (checkbox_rect.right - 5, checkbox_rect.y + 5), 3)
    
    def handle_click(self, pos):
        # Check dropdowns
        if self.mode_rect.collidepoint(pos):
            self.mode_dropdown_open = not self.mode_dropdown_open
            self.site_dropdown_open = False
            self.browser_lib_dropdown_open = False
            self.difficulty_dropdown_open = False
            return
        
        if self.mode_dropdown_open:
            for i, option in enumerate(self.mode_options):
                option_rect = pygame.Rect(self.mode_rect.x, self.mode_rect.bottom + i * 35, self.mode_rect.width, 35)
                if option_rect.collidepoint(pos):
                    self.mode = option
                    self.mode_dropdown_open = False
                    if self.mode != "browser":
                        self.site_dropdown_open = False
                    return
        
        if self.site_rect.collidepoint(pos) and self.mode == "browser":
            self.site_dropdown_open = not self.site_dropdown_open
            self.mode_dropdown_open = False
            self.browser_lib_dropdown_open = False
            self.difficulty_dropdown_open = False
            return
        
        if self.browser_lib_rect.collidepoint(pos) and self.mode == "browser":
            self.browser_lib_dropdown_open = not self.browser_lib_dropdown_open
            self.mode_dropdown_open = False
            self.site_dropdown_open = False
            self.difficulty_dropdown_open = False
            return
        
        if self.browser_lib_dropdown_open:
            for i, option in enumerate(self.browser_lib_options):
                option_rect = pygame.Rect(self.browser_lib_rect.x, self.browser_lib_rect.bottom + i * 35, self.browser_lib_rect.width, 35)
                if option_rect.collidepoint(pos):
                    self.browser_lib = option
                    self.browser_lib_dropdown_open = False
                    return
        
        if self.site_dropdown_open:
            for i, option in enumerate(self.site_options):
                option_rect = pygame.Rect(self.site_rect.x, self.site_rect.bottom + i * 35, self.site_rect.width, 35)
                if option_rect.collidepoint(pos):
                    self.site = option
                    self.site_dropdown_open = False
                    if self.site == "freeminesweeper.org":
                        self.difficulty = "intermediate"
                    return
        
        if self.difficulty_rect.collidepoint(pos):
            self.difficulty_dropdown_open = not self.difficulty_dropdown_open
            self.mode_dropdown_open = False
            self.site_dropdown_open = False
            self.browser_lib_dropdown_open = False
            return
        
        if self.difficulty_dropdown_open:
            for i, option in enumerate(self.difficulty_options):
                option_rect = pygame.Rect(self.difficulty_rect.x, self.difficulty_rect.bottom + i * 35, self.difficulty_rect.width, 35)
                if option_rect.collidepoint(pos):
                    self.difficulty = option
                    self.difficulty_dropdown_open = False
                    return
        
        # Check checkbox
        if self.show_board_rect.collidepoint(pos) and self.mode == "simulated":
            self.show_board = not self.show_board
        
        # Check start button
        if self.start_button_rect.collidepoint(pos):
            self.running = False
        
        # Check if click is within any dropdown option area
        clicked_in_dropdown_options = False
        if self.mode_dropdown_open:
            for i, option in enumerate(self.mode_options):
                option_rect = pygame.Rect(self.mode_rect.x, self.mode_rect.bottom + i * 35, self.mode_rect.width, 35)
                if option_rect.collidepoint(pos):
                    clicked_in_dropdown_options = True
                    break
        if self.site_dropdown_open:
            for i, option in enumerate(self.site_options):
                option_rect = pygame.Rect(self.site_rect.x, self.site_rect.bottom + i * 35, self.site_rect.width, 35)
                if option_rect.collidepoint(pos):
                    clicked_in_dropdown_options = True
                    break
        if self.browser_lib_dropdown_open:
            for i, option in enumerate(self.browser_lib_options):
                option_rect = pygame.Rect(self.browser_lib_rect.x, self.browser_lib_rect.bottom + i * 35, self.browser_lib_rect.width, 35)
                if option_rect.collidepoint(pos):
                    clicked_in_dropdown_options = True
                    break
        if self.difficulty_dropdown_open:
            for i, option in enumerate(self.difficulty_options):
                option_rect = pygame.Rect(self.difficulty_rect.x, self.difficulty_rect.bottom + i * 35, self.difficulty_rect.width, 35)
                if option_rect.collidepoint(pos):
                    clicked_in_dropdown_options = True
                    break
        
        # Close dropdowns if clicking elsewhere (not on dropdown boxes or their options)
        if not clicked_in_dropdown_options and not any([
            self.mode_rect.collidepoint(pos), 
            self.site_rect.collidepoint(pos),
            self.browser_lib_rect.collidepoint(pos),
            self.difficulty_rect.collidepoint(pos),
            self.num_games_rect.collidepoint(pos),
            self.show_board_rect.collidepoint(pos),
            self.start_button_rect.collidepoint(pos)
        ]):
            self.mode_dropdown_open = False
            self.site_dropdown_open = False
            self.browser_lib_dropdown_open = False
            self.difficulty_dropdown_open = False
    
    def handle_text_input(self, event):
        if self.num_games_rect.collidepoint(pygame.mouse.get_pos()):
            if event.key == pygame.K_BACKSPACE:
                self.num_games = self.num_games[:-1] if len(self.num_games) > 0 else ""
            elif event.unicode.isdigit():
                self.num_games += event.unicode
    
    def draw_dropdown_box(self, rect, selected_value, is_open):
        """Draw just the dropdown box without the options menu"""
        color = self.colors['dropdown_hover'] if rect.collidepoint(pygame.mouse.get_pos()) else self.colors['dropdown']
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], rect, 2)
        
        # Draw selected text - truncate if too long
        text_str = str(selected_value)
        arrow_space = 30  # Space reserved for arrow
        max_width = rect.width - 20 - arrow_space  # 10px padding on left, arrow space on right
        
        # Try rendering with regular font first
        text_surface = self.font.render(text_str, True, self.colors['text'])
        
        # If text is too wide, try with smaller font or truncate
        if text_surface.get_width() > max_width:
            # Try with option font (smaller)
            text_surface = self.option_font.render(text_str, True, self.colors['text'])
            
            # If still too wide, truncate with ellipsis
            if text_surface.get_width() > max_width:
                ellipsis = "..."
                while len(text_str) > 0:
                    truncated = text_str[:len(text_str)-1] + ellipsis
                    test_surface = self.option_font.render(truncated, True, self.colors['text'])
                    if test_surface.get_width() <= max_width:
                        text_str = truncated
                        text_surface = test_surface
                        break
                    text_str = text_str[:len(text_str)-1]
        
        text_x = rect.x + 10
        text_y = rect.centery - text_surface.get_height() // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Draw arrow
        arrow_size = 8
        arrow_x = rect.right - 20
        arrow_y = rect.centery
        if is_open:
            pygame.draw.polygon(self.screen, self.colors['text'], 
                              [(arrow_x, arrow_y - arrow_size//2),
                               (arrow_x + arrow_size, arrow_y - arrow_size//2),
                               (arrow_x + arrow_size//2, arrow_y + arrow_size//2)])
        else:
            pygame.draw.polygon(self.screen, self.colors['text'],
                              [(arrow_x, arrow_y + arrow_size//2),
                               (arrow_x + arrow_size, arrow_y + arrow_size//2),
                               (arrow_x + arrow_size//2, arrow_y - arrow_size//2)])
    
    def draw_dropdown_options(self, rect, options, is_open):
        """Draw the dropdown options menu (call this last to appear on top)"""
        if not is_open:
            return
        
        dropdown_height = len(options) * 35
        dropdown_rect = pygame.Rect(rect.x, rect.bottom, rect.width, dropdown_height)
        pygame.draw.rect(self.screen, self.colors['dropdown'], dropdown_rect)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], dropdown_rect, 2)
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(options):
            option_rect = pygame.Rect(rect.x, rect.bottom + i * 35, rect.width, 35)
            
            # Draw background first (hover or normal)
            if option_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, self.colors['dropdown_hover'], option_rect)
            else:
                pygame.draw.rect(self.screen, self.colors['dropdown'], option_rect)
            
            # Then draw text on top
            option_text = self.option_font.render(str(option), True, self.colors['text'])
            option_y = option_rect.centery - option_text.get_height() // 2
            self.screen.blit(option_text, (option_rect.x + 10, option_y))
    
    def draw(self):
        self.screen.fill(self.colors['bg'])
        
        # Title
        title_surface = self.title_font.render("Minesweeper Solver", True, self.colors['text'])
        title_x = (self.width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, 30))
        
        # Mode dropdown box
        mode_label = self.small_font.render("Mode:", True, self.colors['text'])
        self.screen.blit(mode_label, (self.mode_rect.x, self.mode_rect.y - 25))
        self.draw_dropdown_box(self.mode_rect, self.mode, self.mode_dropdown_open)
        
        # Site dropdown box (only for browser mode)
        if self.mode == "browser":
            site_label = self.small_font.render("Website:", True, self.colors['text'])
            self.screen.blit(site_label, (self.site_rect.x, self.site_rect.y - 25))
            self.draw_dropdown_box(self.site_rect, self.site, self.site_dropdown_open)
        else:
            site_label = self.small_font.render("Website:", True, (150, 150, 150))
            self.screen.blit(site_label, (self.site_rect.x, self.site_rect.y - 25))
            disabled_rect = pygame.Rect(self.site_rect.x, self.site_rect.y, self.site_rect.width, self.site_rect.height)
            pygame.draw.rect(self.screen, (220, 220, 220), disabled_rect)
            pygame.draw.rect(self.screen, (180, 180, 180), disabled_rect, 2)
            disabled_text = self.font.render("N/A", True, (150, 150, 150))
            self.screen.blit(disabled_text, (disabled_rect.x + 10, disabled_rect.centery - disabled_text.get_height() // 2))
        
        # Browser library dropdown box (only for browser mode)
        if self.mode == "browser":
            browser_lib_label = self.small_font.render("Browser Library:", True, self.colors['text'])
            self.screen.blit(browser_lib_label, (self.browser_lib_rect.x, self.browser_lib_rect.y - 25))
            self.draw_dropdown_box(self.browser_lib_rect, self.browser_lib, self.browser_lib_dropdown_open)
        else:
            browser_lib_label = self.small_font.render("Browser Library:", True, (150, 150, 150))
            self.screen.blit(browser_lib_label, (self.browser_lib_rect.x, self.browser_lib_rect.y - 25))
            disabled_rect = pygame.Rect(self.browser_lib_rect.x, self.browser_lib_rect.y, self.browser_lib_rect.width, self.browser_lib_rect.height)
            pygame.draw.rect(self.screen, (220, 220, 220), disabled_rect)
            pygame.draw.rect(self.screen, (180, 180, 180), disabled_rect, 2)
            disabled_text = self.font.render("N/A", True, (150, 150, 150))
            self.screen.blit(disabled_text, (disabled_rect.x + 10, disabled_rect.centery - disabled_text.get_height() // 2))
        
        # Difficulty dropdown box
        difficulty_label = self.small_font.render("Difficulty:", True, self.colors['text'])
        self.screen.blit(difficulty_label, (self.difficulty_rect.x, self.difficulty_rect.y - 25))
        if self.mode == "browser" and self.site == "freeminesweeper.org":
            disabled_rect = pygame.Rect(self.difficulty_rect.x, self.difficulty_rect.y, self.difficulty_rect.width, self.difficulty_rect.height)
            pygame.draw.rect(self.screen, (220, 220, 220), disabled_rect)
            pygame.draw.rect(self.screen, (180, 180, 180), disabled_rect, 2)
            disabled_text = self.font.render("Intermediate", True, (150, 150, 150))
            self.screen.blit(disabled_text, (disabled_rect.x + 10, disabled_rect.centery - disabled_text.get_height() // 2))
        else:
            self.draw_dropdown_box(self.difficulty_rect, self.difficulty, self.difficulty_dropdown_open)
        
        # Number of games input
        self.draw_text_input(self.num_games_rect, self.num_games, "Number of Games:")
        
        # Show board checkbox (only for simulated mode)
        if self.mode == "simulated":
            self.draw_checkbox(self.show_board_rect, self.show_board, "Show Board State:")
        else:
            checkbox_label = self.small_font.render("Show Board State:", True, (150, 150, 150))
            self.screen.blit(checkbox_label, (self.show_board_rect.x, self.show_board_rect.y - 25))
            disabled_rect = pygame.Rect(self.show_board_rect.x, self.show_board_rect.y, 30, 30)
            pygame.draw.rect(self.screen, (220, 220, 220), disabled_rect)
            pygame.draw.rect(self.screen, (180, 180, 180), disabled_rect, 2)
        
        # Start button - draw larger background
        mouse_pos = pygame.mouse.get_pos()
        button_hover = self.start_button_rect.collidepoint(mouse_pos)
        button_color = self.colors['button_hover'] if button_hover else self.colors['button']
        
        # Draw button background (fill the entire rect) - width=0 means fill
        pygame.draw.rect(self.screen, button_color, self.start_button_rect, width=0, border_radius=10)
        # Draw border on top
        pygame.draw.rect(self.screen, (50, 50, 50), self.start_button_rect, width=3, border_radius=10)
        
        start_text = self.font.render("START", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(start_text, text_rect)
        
        # Draw dropdown option menus LAST so they appear on top
        self.draw_dropdown_options(self.mode_rect, self.mode_options, self.mode_dropdown_open)
        if self.mode == "browser":
            self.draw_dropdown_options(self.site_rect, self.site_options, self.site_dropdown_open)
            self.draw_dropdown_options(self.browser_lib_rect, self.browser_lib_options, self.browser_lib_dropdown_open)
        if not (self.mode == "browser" and self.site == "freeminesweeper.org"):
            self.draw_dropdown_options(self.difficulty_rect, self.difficulty_options, self.difficulty_dropdown_open)
        
        pygame.display.flip()
    
    def is_mouse_over_dropdown_options(self, pos):
        """Check if mouse is over any dropdown option area"""
        if self.mode_dropdown_open:
            for i, option in enumerate(self.mode_options):
                option_rect = pygame.Rect(self.mode_rect.x, self.mode_rect.bottom + i * 35, self.mode_rect.width, 35)
                if option_rect.collidepoint(pos):
                    return True
        if self.site_dropdown_open:
            for i, option in enumerate(self.site_options):
                option_rect = pygame.Rect(self.site_rect.x, self.site_rect.bottom + i * 35, self.site_rect.width, 35)
                if option_rect.collidepoint(pos):
                    return True
        if self.browser_lib_dropdown_open:
            for i, option in enumerate(self.browser_lib_options):
                option_rect = pygame.Rect(self.browser_lib_rect.x, self.browser_lib_rect.bottom + i * 35, self.browser_lib_rect.width, 35)
                if option_rect.collidepoint(pos):
                    return True
        if self.difficulty_dropdown_open:
            for i, option in enumerate(self.difficulty_options):
                option_rect = pygame.Rect(self.difficulty_rect.x, self.difficulty_rect.bottom + i * 35, self.difficulty_rect.width, 35)
                if option_rect.collidepoint(pos):
                    return True
        return False
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
                
                if event.type == pygame.KEYDOWN:
                    self.handle_text_input(event)
                    if event.key == pygame.K_ESCAPE:
                        return None
            
            self.draw()
            self.clock.tick(60)
        
        # Return configuration
        try:
            num_games_int = int(self.num_games) if self.num_games else 10
        except:
            num_games_int = 10
        
        return {
            'mode': self.mode,
            'site': self.site if self.mode == "browser" else None,
            'browser_lib': self.browser_lib if self.mode == "browser" else None,
            'difficulty': self.difficulty,
            'num_games': num_games_int,
            'show_board': self.show_board if self.mode == "simulated" else False
        }

