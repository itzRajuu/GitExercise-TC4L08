import pygame
import sys
import random

pygame.init()

# Load the starting song
pygame.mixer.music.load('Title_song-1.mp3')
pygame.mixer.music.play(loops=-1)

# Load coin sound
coin_sound = pygame.mixer.Sound('coin_sound.mp3')

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slugterra Game")
main_font = pygame.font.SysFont("cambria", 50)

# Load the background images
background_image = pygame.image.load('Slug.Background.jpg')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_image_2 = pygame.image.load('Earth_elemental.jpg')
background_image_2 = pygame.transform.scale(background_image_2, (SCREEN_WIDTH * 2, SCREEN_HEIGHT))  # Twice as wide for scrolling effect
background_image_2_width = background_image_2.get_width()

# Load and scale the coin image
Fire_coin = pygame.image.load('fire_coin.png').convert_alpha()
Fire_coin = pygame.transform.smoothscale(Fire_coin, (90, 90))

# Load platform images
platform_image = pygame.image.load('platform_image.png').convert_alpha()
platform_image = pygame.transform.scale(platform_image, (200, 100))

# Load slug images
slug1_frames = [
    pygame.image.load("burpy_pose.png").convert_alpha(),
    pygame.image.load("burpy_pose1.png").convert_alpha(),
    pygame.image.load("burpy_pose2.png").convert_alpha(),
]

slug2_frames = [
    pygame.image.load("Frost.png").convert_alpha(),
    pygame.image.load("Frost1.png").convert_alpha(),
    pygame.image.load("Frost2.png").convert_alpha(),
]

# Load enemy slug images
ghoul_slug_frames = [
    pygame.image.load("ghoul_slug.png").convert_alpha(),
    pygame.image.load("ghoul_slug1.png").convert_alpha(),
    pygame.image.load("ghoul_slug2.png").convert_alpha(),
]

# Load slug frames for projectile
slug_projectile_frames = [
    pygame.image.load("slug_projectile1.png").convert_alpha(),
    pygame.image.load("slug_projectile2.png").convert_alpha(),
    pygame.image.load("slug_projectile3.png").convert_alpha(),
]

enemy_image = pygame.image.load("enemy_slug.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (50, 50))

# Initialize slug settings
current_slug = 1
slug_frames = slug1_frames
slug_frame_index = 0
slug_frame_rate = 10  # Speed of slug animation
slug_frame_counter = 0

# Projectile settings
projectile_speed = 10
player_projectiles = []
enemy_projectiles = []

# Enemy settings
enemy_size = 50
enemies = []
enemy_projectile_speed = 7
enemy_shoot_interval = 60  # Adjust shooting speed
enemy_speed = 1
enemy_gravity = 0.5

# Player settings
player_size = 50
player_speed = 6
player_direction = 1  # Direction the player is facing: 1 for right, -1 for left

# Player health
player_health = 3
max_health = 3

# Gravity settings
gravity = 0.5
jump_strength = -10

# Initialize player variables
player = pygame.Rect((300, 250, player_size, player_size))
player_y_velocity = 0  # Vertical velocity for jumping
can_jump = True
can_double_jump = True

# Create a list to hold platform rects
platforms = []
platform_spawn_x = SCREEN_WIDTH  # Start spawning platforms from the right edge
platform_spawn_distance = 300  # Minimum distance between platform spawns
platform_spacing = 200  # Maximum vertical spacing between platforms
platform_timer = pygame.time.get_ticks()  # Start the timer
platform_spawn_delay = 2000  # 2 seconds delay between each platform spawn

# Create a list to hold coin rects
coins = []
coin_spawn_delay = 1500  # 1.5-second delay between each coin spawn
coin_timer = pygame.time.get_ticks()  # Start the timer

def create_platform(x, y):
    platform_rect = platform_image.get_rect(topleft=(x, y))
    platforms.append(platform_rect)
    # Optionally create a coin on the platform
    create_coin(platform_rect)

def create_coin(platform):
    coin_rect = Fire_coin.get_rect(center=(platform.centerx, platform.top - 10))
    coins.append(coin_rect)

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

# Background scrolling variables
background_scroll = 0
allow_left_scroll = False
scroll_limit = 600  # Limit after which the background starts scrolling
score = 0

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

# Load button image and create a button
button_surface = pygame.image.load("button.png")
button_surface = pygame.transform.scale(button_surface, (300, 150))
button = Button(button_surface, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 250, "Start")

# Projectile class
class Projectile:
    def __init__(self, x, y, speed, direction, frames):
        self.rect = pygame.Rect(x, y, 30, 15)  # Adjust size if needed
        self.speed = speed
        self.direction = direction  # 1 for right, -1 for left
        self.frames = frames
        self.frame_index = 0
        self.frame_counter = 0
        self.frame_rate = 10  # Speed of animation frames

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            return False  # Off-screen
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        return True

    def draw(self, screen):
        screen.blit(self.frames[self.frame_index], self.rect.topleft)

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, enemy_size, enemy_size)
        self.shoot_timer = 0  # Timer to control shooting intervals
        self.hit_count = 0  # Track how many times the enemy has been hit
        self.y_velocity = 0  # Vertical velocity for gravity
        self.frames = ghoul_slug_frames
        self.frame_index = 0
        self.frame_counter = 0
        self.frame_rate = 10

    def update(self, player_x):
        if self.rect.x < player_x:
            self.rect.x += enemy_speed
        elif self.rect.x > player_x:
            self.rect.x -= enemy_speed
        
        # Apply gravity to enemy
        self.y_velocity += enemy_gravity
        self.rect.y += self.y_velocity

        # Collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.y_velocity > 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                break

        # Prevent the enemy from falling below the screen
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y_velocity = 0

        self.shoot_timer += 1
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, screen):
        screen.blit(self.frames[self.frame_index], self.rect.topleft)

    def shoot(self, player_x, player_y):
        if self.shoot_timer >= enemy_shoot_interval:
            self.shoot_timer = 0
            direction = 1 if player_x >= self.rect.x else -1
            return Projectile(self.rect.x, self.rect.y + self.rect.height // 2, enemy_projectile_speed, direction, slug_projectile_frames)
        return None

# Initialize enemies
enemies.append(Enemy(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150))  # Adjusted initial position

# Main Game
run = True
game_active = False 

# Track if the space bar was pressed
space_pressed = False

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False
    
    # Background scrolling
    background_scroll -= 5
    if background_scroll <= -background_image_2_width:
        background_scroll = 0

    # Update game elements
    for enemy in enemies:
        enemy.update(player.x)
        projectile = enemy.shoot(player.x, player.y)
        if projectile:
            enemy_projectiles.append(projectile)
    
    for projectile in player_projectiles:
        if not projectile.update():
            player_projectiles.remove(projectile)

    for projectile in enemy_projectiles:
        if not projectile.update():
            enemy_projectiles.remove(projectile)

    # Drawing
    screen.blit(background_image, (background_scroll, 0))
    screen.blit(background_image_2, (background_scroll, 0))
    screen.blit(background_image_2, (background_scroll + SCREEN_WIDTH, 0))
    
    # Draw platforms
    for platform in platforms:
        screen.blit(platform_image, platform.topleft)
    
    # Draw coins
    for coin in coins:
        screen.blit(Fire_coin, coin.topleft)

    # Draw player
    pygame.draw.rect(screen, (0, 0, 255), player)  # Draw player as blue rectangle for now

    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen)

    # Draw projectiles
    for projectile in player_projectiles:
        projectile.draw(screen)
    
    for projectile in enemy_projectiles:
        projectile.draw(screen)

    # Draw health bar
    health_bar(screen, 10, 10, player_health, max_health)
    
    # Draw button
    button.update()

    pygame.display.flip()
    pygame.time.Clock().tick(60)
