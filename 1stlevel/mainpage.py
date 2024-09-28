import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

# Load background image and music
background = pygame.image.load('Slug.Background.jpg')
pygame.mixer.music.load('Title_song.mp3')
pygame.mixer.music.play(-1)

# Button properties
button_font = pygame.font.Font(None, 74)
button_text = button_font.render("Start", True, WHITE)
button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

def main_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    level_selection()

        # Draw the background and button
        screen.blit(background, (0, 0))
        screen.blit(button_text, button_rect)
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def level_selection():
    level_files = [f for f in os.listdir('levels') if f.endswith('.py')]
    selected_level = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_level = (selected_level + 1) % len(level_files)
                if event.key == pygame.K_UP:
                    selected_level = (selected_level - 1) % len(level_files)
                if event.key == pygame.K_RETURN:
                    run_level(level_files[selected_level])

        # Draw the level selection screen
        screen.fill((0, 0, 0))
        title_font = pygame.font.Font(None, 74)
        title_text = title_font.render("Select Level", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        # Draw level options
        for i, level_file in enumerate(level_files):
            if i == selected_level:
                color = (255, 0, 0)
            else:
                color = WHITE
            level_text = button_font.render(level_file[:-3], True, color)
            screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 150 + i * 60))

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def run_level(level_file):
    # Here you would import and run the level Python file
    # Example: `import levels.level1`
    exec(open(os.path.join('levels', level_file)).read())

if __name__ == "__main__":
    main_menu()
