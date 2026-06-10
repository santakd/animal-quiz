#!/usr/bin/env python3
"""
animal_quiz.py - Animal Quiz Show
Pygame application utilizing SQLite BLOBs and Pillow for animated GIF rendering.
Version: 1.0.8

"""
# imports
import os
import sys
import sqlite3
import logging
import hashlib
import random
import io
from pathlib import Path
from datetime import datetime

import pygame
from PIL import Image, ImageSequence

# ==========================================
# CONFIGURATION
# ==========================================
# Directory Structure
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "db" / "animal_quiz.sqlite"
LOG_DIR = BASE_DIR / "logs"

# Game Settings
QUESTIONS_PER_GAME = 10
DELAY_AFTER_ANSWER_MS = 2000  # 2 seconds
FPS = 60

# Display Configuration (Increased height to prevent overlap with 512px images)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 860

# Colors (R, G, B)
COLOR_BG = (243, 244, 246)
COLOR_TEXT = (31, 41, 55)
COLOR_PRIMARY = (79, 70, 229)
COLOR_PRIMARY_HOVER = (67, 56, 202)
COLOR_SUCCESS = (34, 197, 94)
COLOR_ERROR = (239, 68, 68)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (209, 213, 219)

# ==========================================
# LOGGING SETUP
# ==========================================
def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"animal_quiz_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("AnimalQuiz")

logger = setup_logging()

# ==========================================
# HELPER CLASSES
# ==========================================
class AnimatedGIF:
    """Handles extracting frames from a GIF BLOB via Pillow and animating in Pygame."""
    def __init__(self, blob_data, center_pos):
        self.frames = []
        self.durations = []
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.rect = None
        self.center_pos = center_pos
        self.valid = False
        
        self._load_from_blob(blob_data)

    def _load_from_blob(self, blob_data):
        try:
            byte_stream = io.BytesIO(blob_data)
            pil_image = Image.open(byte_stream)
            
            for frame in ImageSequence.Iterator(pil_image):
                frame_rgba = frame.convert("RGBA")
                mode = frame_rgba.mode
                size = frame_rgba.size
                data = frame_rgba.tobytes()
                
                pg_image = pygame.image.fromstring(data, size, mode)
                self.frames.append(pg_image)
                self.durations.append(frame.info.get('duration', 100)) # Default 100ms
                
            if self.frames:
                self.rect = self.frames[0].get_rect(center=self.center_pos)
                self.valid = True
                
        except Exception as e:
            logger.error(f"Failed to decode animated GIF BLOB: {e}")

    def update(self):
        if not self.valid or len(self.frames) <= 1:
            return
        now = pygame.time.get_ticks()
        if now - self.last_update > self.durations[self.current_frame]:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now

    def draw(self, surface):
        if self.valid:
            surface.blit(self.frames[self.current_frame], self.rect)

class Button:
    """UI Clickable Button."""
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = COLOR_PRIMARY
        self.is_hovered = False
        self.disabled = False
        
    def draw(self, surface):
        current_color = COLOR_GRAY if self.disabled else (COLOR_PRIMARY_HOVER if self.is_hovered else self.color)
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        
        text_surf = self.font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        if not self.disabled:
            self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class TextInput:
    """Simple Pygame Text Input Box."""
    def __init__(self, x, y, w, h, font, is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_GRAY
        self.text = ''
        self.font = font
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = COLOR_PRIMARY if self.active else COLOR_GRAY
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20:
                    self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 2, border_radius=4)
        display_text = '*' * len(self.text) if self.is_password else self.text
        text_surface = self.font.render(display_text, True, COLOR_TEXT)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

# ==========================================
# MAIN APPLICATION MANAGER
# ==========================================
class AnimalQuizApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Animal Quiz Show")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.SysFont('segoeui', 48, bold=True)
        self.font = pygame.font.SysFont('segoeui', 28)
        self.small_font = pygame.font.SysFont('segoeui', 20)
        
        # State Management
        self.state = "LOGIN"
        self.running = True
        
        # Database setup
        self.conn = None
        self._connect_db()
        
        # Login UI - Adjusted Y positions for taller window
        self.input_user = TextInput(SCREEN_WIDTH//2 - 150, 280, 300, 40, self.font)
        self.input_pass = TextInput(SCREEN_WIDTH//2 - 150, 370, 300, 40, self.font, is_password=True)
        self.btn_login = Button(SCREEN_WIDTH//2 - 150, 460, 300, 50, "Login", self.font)
        self.login_error = ""

        # Quiz State
        self.all_animals = []
        self.quiz_questions = []
        self.current_q_index = 0
        self.score = 0
        self.current_gif = None
        self.buttons = []
        self.delay_start_time = 0
        self.feedback_message = ""

    def _connect_db(self):
        if not DB_FILE.exists():
            logger.critical("Database not found. Please run setup_db.py first.")
            sys.exit(1)
        try:
            self.conn = sqlite3.connect(DB_FILE)
            logger.info("Successfully connected to database.")
        except Exception as e:
            logger.critical(f"Database connection failed: {e}")
            sys.exit(1)

    def _hash_password(self, pwd: str) -> str:
        return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

    def handle_login(self):
        user = self.input_user.text.strip()
        pwd = self.input_pass.text.strip()
        hashed_pwd = self._hash_password(pwd)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM app_users WHERE username=? AND password_hash=?", (user, hashed_pwd))
            result = cursor.fetchone()
            
            if result:
                logger.info(f"User '{user}' authenticated successfully.")
                self.load_game_data()
                self.state = "START"
            else:
                self.login_error = "Invalid username or password"
                logger.warning(f"Failed login attempt for user: '{user}'")
        except Exception as e:
            logger.error(f"Login database error: {e}")
            self.login_error = "Database Error"

    def load_game_data(self):
        """Loads animal names and BLOBs into memory for the quiz."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT animal_name, image_blob FROM animals")
            self.all_animals = cursor.fetchall()
            logger.info(f"Loaded {len(self.all_animals)} animals from database.")
        except Exception as e:
            logger.error(f"Failed to fetch animals: {e}")
            
    def start_quiz(self):
        if len(self.all_animals) < 4:
            logger.error("Not enough animals in DB to start the quiz. Need at least 4.")
            self.running = False
            return
            
        self.score = 0
        self.current_q_index = 0
        self.feedback_message = ""
        
        # Pick random questions
        pool = random.sample(self.all_animals, min(QUESTIONS_PER_GAME, len(self.all_animals)))
        self.quiz_questions = []
        
        for correct_animal in pool:
            correct_name = correct_animal[0]
            blob = correct_animal[1]
            
            wrong_pool = [a[0] for a in self.all_animals if a[0] != correct_name]
            
            # Ensure there are enough wrong choices
            if len(wrong_pool) < 3:
                logger.error(f"Not enough unique animals to generate 3 wrong choices for '{correct_name}'. Skipping question.")
                continue 

            wrong_choices = random.sample(wrong_pool, 3)
            
            choices = wrong_choices + [correct_name]
            random.shuffle(choices)
            
            self.quiz_questions.append({
                "correct": correct_name,
                "blob": blob,
                "choices": choices
            })
        
        if not self.quiz_questions:
            logger.critical("No valid questions could be generated. Exiting.")
            self.running = False
            return
            
        self.load_question()
        self.state = "QUIZ"

    def load_question(self):
        q = self.quiz_questions[self.current_q_index]
        # Shifted GIF center down slightly for taller screen
        self.current_gif = AnimatedGIF(q['blob'], (SCREEN_WIDTH // 2, 320))
        
        # Create buttons
        self.buttons = []
        btn_width = 300
        btn_height = 50
        gap = 20
        # Start buttons further down to accommodate 512px GIFs
        start_y = 620 
        
        # 2x2 Grid for buttons
        positions = [
            (SCREEN_WIDTH//2 - btn_width - gap//2, start_y),
            (SCREEN_WIDTH//2 + gap//2, start_y),
            (SCREEN_WIDTH//2 - btn_width - gap//2, start_y + btn_height + gap),
            (SCREEN_WIDTH//2 + gap//2, start_y + btn_height + gap)
        ]
        
        for i, choice in enumerate(q['choices']):
            self.buttons.append(Button(positions[i][0], positions[i][1], btn_width, btn_height, choice, self.font))

    def evaluate_answer(self, selected_button):
        q = self.quiz_questions[self.current_q_index]
        is_correct = (selected_button.text == q['correct'])
        
        if is_correct:
            selected_button.color = COLOR_SUCCESS
            self.score += 1
        else:
            selected_button.color = COLOR_ERROR
            # Highlight correct answer
            for btn in self.buttons:
                if btn.text == q['correct']:
                    btn.color = COLOR_SUCCESS
                    
        for btn in self.buttons:
            btn.disabled = True
            
        self.delay_start_time = pygame.time.get_ticks()
        self.state = "DELAY"

    def _calculate_feedback_message(self):
        """Calculates the feedback message based on the quiz score percentage. Emojis removed for Pygame font safety."""
        total_questions = len(self.quiz_questions)
        if total_questions == 0:
            self.feedback_message = "No questions were played."
            return

        percentage = self.score / total_questions
        if percentage == 1:
            self.feedback_message = "Perfect score! You are an animal expert!"
        elif percentage >= 0.7:
            self.feedback_message = "Great job! You really know your animals!"
        elif percentage >= 0.5:
            self.feedback_message = "Not bad! But there's room for improvement."
        else:
            self.feedback_message = "Keep practicing! You'll get them next time."
            
        logger.info(f"Quiz ended. Score: {self.score}/{total_questions}. Feedback: {self.feedback_message}")

    def run(self):
        """Main non-blocking event loop."""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if self.state == "LOGIN":
                    self.input_user.handle_event(event)
                    self.input_pass.handle_event(event)
                    self.btn_login.check_hover(mouse_pos)
                    if self.btn_login.handle_event(event):
                        self.handle_login()
                        
                elif self.state == "START":
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        self.start_quiz()
                        
                elif self.state == "QUIZ":
                    for btn in self.buttons:
                        btn.check_hover(mouse_pos)
                        if btn.handle_event(event):
                            self.evaluate_answer(btn)
                            
                elif self.state == "RESULT":
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        self.state = "START"

            self.update_logic()
            self.draw_screen()
            self.clock.tick(FPS)
            
        self.cleanup()

    def update_logic(self):
        if self.state in ["QUIZ", "DELAY"]:
            if self.current_gif:
                self.current_gif.update()
                
        if self.state == "DELAY":
            if pygame.time.get_ticks() - self.delay_start_time > DELAY_AFTER_ANSWER_MS:
                self.current_q_index += 1
                if self.current_q_index < len(self.quiz_questions):
                    self.load_question()
                    self.state = "QUIZ"
                else:
                    self._calculate_feedback_message() 
                    self.state = "RESULT"

    def draw_screen(self):
        self.screen.fill(COLOR_BG)
        
        if self.state == "LOGIN":
            title = self.title_font.render("Animal Quiz Admin Login", True, COLOR_PRIMARY)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 150)))
            
            lbl_u = self.small_font.render("Username:", True, COLOR_TEXT)
            self.screen.blit(lbl_u, (SCREEN_WIDTH//2 - 150, 250))
            self.input_user.draw(self.screen)
            
            lbl_p = self.small_font.render("Password:", True, COLOR_TEXT)
            self.screen.blit(lbl_p, (SCREEN_WIDTH//2 - 150, 340))
            self.input_pass.draw(self.screen)
            
            self.btn_login.draw(self.screen)
            
            if self.login_error:
                err = self.small_font.render(self.login_error, True, COLOR_ERROR)
                self.screen.blit(err, err.get_rect(center=(SCREEN_WIDTH//2, 550)))

        elif self.state == "START":
            title = self.title_font.render("Animal Quiz Show", True, COLOR_PRIMARY)
            sub = self.font.render("Press any key to start...", True, COLOR_TEXT)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 350)))
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, 450)))
            
        elif self.state in ["QUIZ", "DELAY"]:
            prog = self.small_font.render(f"Question {self.current_q_index + 1} of {len(self.quiz_questions)}", True, COLOR_TEXT)
            self.screen.blit(prog, (20, 20))
            
            if self.current_gif:
                self.current_gif.draw(self.screen)
                
            for btn in self.buttons:
                btn.draw(self.screen)
                
        elif self.state == "RESULT":
            title = self.title_font.render("Quiz Complete!", True, COLOR_PRIMARY)
            score_txt = self.title_font.render(f"{self.score} / {len(self.quiz_questions)}", True, COLOR_TEXT)
            feedback_surf = self.font.render(self.feedback_message, True, COLOR_TEXT)
            sub = self.font.render("Press any key to play again", True, COLOR_GRAY)
            
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 250))) 
            self.screen.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH//2, 350))) 
            self.screen.blit(feedback_surf, feedback_surf.get_rect(center=(SCREEN_WIDTH//2, 450))) 
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, 600)))

        pygame.display.flip()

    def cleanup(self):
        logger.info("Closing application and releasing resources.")
        if self.conn:
            self.conn.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = AnimalQuizApp()
    app.run()