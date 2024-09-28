import pygame
import sys
import time

pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slugterra Game")

# Load background images
start_background_image = pygame.image.load('Slug.Background.jpg')
start_background_image = pygame.transform.scale(start_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_background_image = pygame.image.load('background.png')  # Second background image
game_background_image = pygame.transform.scale(game_background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and scale the button image
button_surface = pygame.image.load("button.png")
button_surface = pygame.transform.scale(button_surface, (400, 150))

# Fonts
main_font = pygame.font.SysFont("cambria", 50)
font = pygame.font.Font(None, 36)

# Character properties
player_size = 50
player_x = (SCREEN_WIDTH - player_size) // 2
player_y = SCREEN_HEIGHT - 2 * player_size
player_speed = 5  # Horizontal speed
player_speed_y = 0  # Vertical speed for jumping
gravity = 0.5
jump = -10
ground_level = SCREEN_HEIGHT - player_size
max_jumps = 2
current_jumps = 0
player_health = 3
max_health = 3

# Projectile settings
projectile_speed = 10
player_projectiles = []
enemy_projectiles = []

# Enemy settings
enemy_size = 50
enemies = []
enemy_speed = 1
enemies.append(pygame.Rect(SCREEN_WIDTH - 100, ground_level, enemy_size, enemy_size))  # Add an enemy

# Load standing image
character_standing = pygame.image.load("character/character_standing.png")

# Load right key animation frames from PNG
gif_forward = ["character/GameWalk1.png", "character/GameWalk2.png"]  # List of PNG files
video_frames_forward = [pygame.image.load(file).convert_alpha() for file in gif_forward]

# Load left key animation frames from PNG
gif_backward = ["character/GameWalkLeft1.png", "character/GameWalkLeft2.png"]  # List of PNG files
video_frames_backward = [pygame.image.load(file).convert_alpha() for file in gif_backward]

# Platform settings
platforms = []
platform_image = pygame.image.load("platform.png")
platform_image = pygame.transform.scale(platform_image, (150, 50))
platforms.append(pygame.Rect(300, ground_level - 60, 150, 50))  # Example platform
platforms.append(pygame.Rect(600, ground_level - 120, 150, 50))  # Example platform

# Coin settings
coin_image = pygame.image.load("coin.png")
coin_image = pygame.transform.scale(coin_image, (30, 30))
coins = [pygame.Rect(350, ground_level - 100, 30, 30), pygame.Rect(650, ground_level - 160, 30, 30)]  # Example coins

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
        if self.rect.collidepoint(position):
            return True
        return False

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
    fill_color = (255, 0, 0)  # Red color for health
    border_color = (0, 0, 0)  # Black color for the border

    # Draw the border of the health bar
    pygame.draw.rect(screen, border_color, (x, y, bar_width, bar_height))
    # Draw the fill of the health bar
    fill_width = (health / max_health) * bar_width
    pygame.draw.rect(screen, fill_color, (x, y, fill_width, bar_height))

# Main loop
run = True
game_active = False  # Variable to track whether the game has started
clock = pygame.time.Clock()

# Character movement and animation properties
character_rect = character_standing.get_rect(bottomleft=(player_x, player_y))  # Set initial position
velocity = 5
frame_index_forward = 0
frame_index_backward = 0
animation_speed = 7  # Number of frames per second for animation
time_per_frame = 1000 // animation_speed  # Time per frame in milliseconds
is_moving_forward = False
is_moving_backward = False
last_frame_time_forward = pygame.time.get_ticks()  # Initialize time tracker for forward movement
last_frame_time_backward = pygame.time.get_ticks()  # Initialize time tracker for backward movement

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button.checkForInput(pygame.mouse.get_pos()) and not game_active:
                game_active = True  # Start the game when the button is clicked
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and current_jumps < max_jumps:
                player_speed_y = jump  # Initiate jump
                current_jumps += 1
            if event.key == pygame.K_SPACE and game_active:
                # Shoot a projectile from the player's current position
                projectile = pygame.Rect(player_x + (player_size // 2), player_y + player_size // 2, 15, 5)
                player_projectiles.append(projectile)
            if event.key == pygame.K_RIGHT:
                is_moving_forward = True
                is_moving_backward = False
                frame_index_forward = 0  # Reset frame index
                last_frame_time_forward = pygame.time.get_ticks()  # Reset time tracker
            elif event.key == pygame.K_LEFT:
                is_moving_backward = True
                is_moving_forward = False
                frame_index_backward = 0  # Reset frame index
                last_frame_time_backward = pygame.time.get_ticks()  # Reset time tracker
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                is_moving_forward = False
            elif event.key == pygame.K_LEFT:
                is_moving_backward = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    # Apply gravity
    player_speed_y += gravity
    player_y += player_speed_y

    # Prevent player from falling below the ground
    if player_y >= ground_level:
        player_y = ground_level
        player_speed_y = 0
        current_jumps = 0  # Reset jump count

    # Update player rect for collision
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    character_rect.bottomleft = (player_x, player_y)

    # Clear the screen
    screen.fill('white')

    if not game_active:
        # Display the start background and start button
        screen.blit(start_background_image, (0, 0))
        button.changeColour(pygame.mouse.get_pos())
        button.update()
    else:
        # Display the game background after the game starts
        screen.blit(game_background_image, (0, 0))

        # Draw platforms
        for platform in platforms:
            screen.blit(platform_image, platform.topleft)

        # Draw coins
        for coin in coins[:]:
            screen.blit(coin_image, coin.topleft)
            # Check collision with player
            if player_rect.colliderect(coin):
                coins.remove(coin)  # Remove coin when collected
                # Optionally, increase player health or score here

        # Draw player with animation
        if is_moving_forward:
            current_time = pygame.time.get_ticks()
            if current_time - last_frame_time_forward > time_per_frame:
                frame_index_forward = (frame_index_forward + 1) % len(video_frames_forward)  # Loop through frames
                last_frame_time_forward = current_time
            screen.blit(video_frames_forward[frame_index_forward], character_rect)
            character_rect.x += velocity

        elif is_moving_backward:
            current_time = pygame.time.get_ticks()
            if current_time - last_frame_time_backward > time_per_frame:
                frame_index_backward = (frame_index_backward + 1) % len(video_frames_backward)  # Loop through frames
                last_frame_time_backward = current_time
            screen.blit(video_frames_backward[frame_index_backward], character_rect)
            character_rect.x -= velocity

        else:
            # If not moving, show the standing image
            screen.blit(character_standing, character_rect)

        # Update and draw player projectiles
        for projectile in player_projectiles[:]:
            projectile.x += projectile_speed
            if projectile.x > SCREEN_WIDTH:
                player_projectiles.remove(projectile)  # Remove the projectile if it goes off-screen
            pygame.draw.rect(screen, 'red', projectile)

        # Update and draw enemies
        for enemy in enemies[:]:
            # Move enemy towards the player
            if enemy.x < player_x:
                enemy.x += enemy_speed
            elif enemy.x > player_x:
                enemy.x -= enemy_speed

            pygame.draw.rect(screen, 'green', enemy)

            # Enemy shooting logic
            if enemy.x == player_x and enemy.y == player_y:
                cutscene("You got hit by an enemy!", screen)
                run = False  # End the game or handle it differently

            # Check collision with projectiles
            for projectile in player_projectiles[:]:
                if projectile.colliderect(enemy):
                    enemies.remove(enemy)
                    player_projectiles.remove(projectile)
                    cutscene("Enemy defeated!", screen)
                    break

        # Draw the health bar
        health_bar(screen, 10, 10, player_health, max_health)

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
sys.exit()
