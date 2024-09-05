import pygame
import sys
import time

pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slugterra Game")

# Load images
start_background_image = pygame.image.load('Slug.Background.jpg')
start_background_image = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_background_image = pygame.image.load('background.png')
game_background_image = pygame.transform.scale(game_background_image, (1280, 1000))
ground_surface_image = pygame.image.load('ground_surface.png')
ground_surface_image = pygame.transform.scale(ground_surface_image, (1280, 100))
button_surface = pygame.image.load("button.png")
button_surface = pygame.transform.scale(button_surface, (400, 150))

# Fonts
main_font = pygame.font.SysFont("cambria", 50)
font = pygame.font.Font(None, 36)

# Character properties
player_size = 200  # Increased size of the character
player_x = 50  # Starting 50 pixels from the left edge
player_y = SCREEN_HEIGHT - player_size - 100  # 100 pixels above the bottom of the screen
player_speed = 3
player_speed_y = 0
gravity = 0.5
jump = -10
ground_level = SCREEN_HEIGHT - 200  # Adjusted ground level
max_jumps = 2
current_jumps = 0
player_health = 33
max_health = 3

# Load images for character
character_standing = pygame.image.load("character/character_standing.png")
character_standing = pygame.transform.scale(character_standing, (player_size, player_size))
gif_forward = ["character/GameWalk1.png", "character/GameWalk2.png"]
video_frames_forward = [pygame.image.load(file).convert_alpha() for file in gif_forward]
video_frames_forward = [pygame.transform.scale(frame, (player_size, player_size)) for frame in video_frames_forward]
gif_backward = ["character/GameWalkLeft1.png", "character/GameWalkLeft2.png"]
video_frames_backward = [pygame.image.load(file).convert_alpha() for file in gif_backward]
video_frames_backward = [pygame.transform.scale(frame, (player_size, player_size)) for frame in video_frames_backward]

# Button class
class Button():
    def __init__(self, image, x_pos, y_pos, text_input):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_input = text_input
        self.text = main_font.render(self.text_input, True, "white")
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
    
    def update(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColour(self, position):
        if self.rect.collidepoint(position):
            self.text = main_font.render(self.text_input, True, "green")
        else:
            self.text = main_font.render(self.text_input, True, "white")

# Create the start button
button = Button(button_surface, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200, "Start")

# Cutscene function
def cutscene(dialogue, screen, top_bar_height=150, delay=0.05):
    running = True
    text_displayed = ""
    clock = pygame.time.Clock()

    for char in dialogue:
        text_displayed += char
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.draw.rect(screen, 'black', (0, 0, SCREEN_WIDTH, top_bar_height))
        text_surface = font.render(text_displayed, True, 'white')
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, top_bar_height // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        time.sleep(delay)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                running = False

        pygame.draw.rect(screen, 'black', (0, 0, SCREEN_WIDTH, top_bar_height))
        text_surface = font.render(text_displayed, True, 'white')
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, top_bar_height // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

# Health bar function
def health_bar(screen, x, y, health, max_health):
    bar_width = 200
    bar_height = 10
    fill_color = (255, 0, 0)
    border_color = (0, 0, 0)
    pygame.draw.rect(screen, border_color, (x, y, bar_width, bar_height))
    fill_width = (health / max_health) * bar_width
    pygame.draw.rect(screen, fill_color, (x, y, fill_width, bar_height))

# Movement settings
background_x = 0
ground_x = 0

# Main loop
run = True
game_active = False
clock = pygame.time.Clock()

# Character movement and animation properties
character_rect = character_standing.get_rect(bottomleft=(player_x, player_y))
velocity = 3
frame_index_forward = 0
frame_index_backward = 0
animation_speed = 5
time_per_frame = 1000 // animation_speed
is_moving_forward = False
is_moving_backward = False
last_frame_time_forward = pygame.time.get_ticks()
last_frame_time_backward = pygame.time.get_ticks()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button.checkForInput(pygame.mouse.get_pos()) and not game_active:
                game_active = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and current_jumps < max_jumps:
                player_speed_y = jump
                current_jumps += 1
            if event.key == pygame.K_RIGHT:
                is_moving_forward = True
                is_moving_backward = False
                frame_index_forward = 0
                last_frame_time_forward = pygame.time.get_ticks()
            elif event.key == pygame.K_LEFT:
                is_moving_backward = True
                is_moving_forward = False
                frame_index_backward = 0
                last_frame_time_backward = pygame.time.get_ticks()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                is_moving_forward = False
            elif event.key == pygame.K_LEFT:
                is_moving_backward = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
        background_x += player_speed * 2
        ground_x += player_speed * 2
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
        background_x -= player_speed * 2
        ground_x -= player_speed * 2

    # Ensure character stays within the screen bounds
    player_x = max(0, min(SCREEN_WIDTH - player_size, player_x))
    player_y = max(0, min(SCREEN_HEIGHT - player_size, player_y))

    # Apply gravity
    player_speed_y += gravity
    player_y += player_speed_y

    # Prevent player from falling below the ground
    if player_y >= ground_level:
        player_y = ground_level
        player_speed_y = 0
        current_jumps = 0

    # Update player rect
    character_rect.bottomleft = (player_x, player_y)

    # Clear the screen
    screen.fill('white')

    if not game_active:
        # Display the start background and start button
        screen.blit(start_background_image, (0, 0))
        button.changeColour(pygame.mouse.get_pos())
        button.update()
    else:
        # Draw the moving background
        screen.blit(game_background_image, (background_x % SCREEN_WIDTH, 0))
        screen.blit(game_background_image, (background_x % SCREEN_WIDTH - SCREEN_WIDTH, 0))

        # Draw the ground surface
        screen.blit(ground_surface_image, (ground_x % SCREEN_WIDTH, ground_level))
        screen.blit(ground_surface_image, (ground_x % SCREEN_WIDTH - SCREEN_WIDTH, ground_level))

        # Draw player with animation
        if is_moving_forward:
            current_time = pygame.time.get_ticks()
            if current_time - last_frame_time_forward >= time_per_frame:
                frame_index_forward = (frame_index_forward + 1) % len(video_frames_forward)
                last_frame_time_forward = current_time
            screen.blit(video_frames_forward[frame_index_forward], character_rect)
        elif is_moving_backward:
            current_time = pygame.time.get_ticks()
            if current_time - last_frame_time_backward >= time_per_frame:
                frame_index_backward = (frame_index_backward + 1) % len(video_frames_backward)
                last_frame_time_backward = current_time
            screen.blit(video_frames_backward[frame_index_backward], character_rect)
        else:
            screen.blit(character_standing, character_rect)

        # Draw the health bar
        health_bar(screen, 10, 10, player_health, max_health)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
