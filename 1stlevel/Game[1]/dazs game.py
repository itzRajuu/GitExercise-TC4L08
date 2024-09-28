import pygame
import sys
import random
import os

os.chdir('C:/Users/Admin/projects/GitExercise-TC4L08')

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

# Load and scale the bullet image
bullet_image = pygame.image.load('fire_bullet1.png').convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (100, 20))  # Adjust size as needed

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
    def __init__(self, x, y, speed, direction):
        self.rect = pygame.Rect(x, y, 15, 5)
        self.speed = speed
        self.direction = direction  # 1 for right, -1 for left

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            return False  # Off-screen
        return True

    def draw(self, screen):
        screen.blit(bullet_image, self.rect.topleft)  # Draw the bullet image

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, enemy_size, enemy_size)
        self.shoot_timer = 0  # Timer to control shooting intervals
        self.hit_count = 0  # Track how many times the enemy has been hit
        self.y_velocity = 0  # Vertical velocity for gravity

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

    def draw(self, screen):
        pygame.draw.rect(screen, 'green', self.rect)

    def shoot(self, player_x, player_y):
        if self.shoot_timer >= enemy_shoot_interval:
            self.shoot_timer = 0
            direction = 1 if player_x >= self.rect.x else -1
            return Projectile(self.rect.x, self.rect.y + self.rect.height // 2, enemy_projectile_speed, direction)
        return None

# Initialize enemies
enemies.append(Enemy(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150))  # Adjusted initial position

# Main Game
run = True
game_active = False 

# Track if the space bar was pressed
space_pressed = False

# Platform spawning logic
def spawn_initial_platforms():
    for _ in range(5):  # Spawn a few initial platforms
        x = random.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - 200)
        y = SCREEN_HEIGHT - random.randint(100, 300)
        create_platform(x, y)

def spawn_new_platforms():
    global platform_spawn_x  # Declare as global to modify the variable
    # Check if the player is near the end of the screen
    if player.right > platform_spawn_x - SCREEN_WIDTH:
        platform_spawn_x += platform_spawn_distance
        x = platform_spawn_x
        y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 100)
        create_platform(x, y)

while run:
    screen.fill((0, 0, 0))  

    if not game_active:
        # Display the starting background and start button
        screen.blit(background_image, (0, 0))
        button.changeColour(pygame.mouse.get_pos())
        button.update()
    else:
        # Stop the song when the game becomes active
        pygame.mixer.music.stop()

        # Game logic
        key = pygame.key.get_pressed()

        # Move player and scroll background when moving right
        if key[pygame.K_d]:
            if player.right < scroll_limit:
                player.move_ip(player_speed, 0)
            else:
                background_scroll -= player_speed  # Background moves to the left
                for platform in platforms:
                    platform.x -= player_speed  # Move platforms to the left

        # Allow moving left only if player is far enough
        elif key[pygame.K_a]:
            if player.left > 0:
                player.move_ip(-player_speed, 0)
            elif background_scroll < 0:  # Stop scrolling when background is at its limit
                background_scroll += player_speed  # Move background right
                for platform in platforms:
                    platform.x += player_speed  # Move platforms to the right
        
        # Jumping logic
        if key[pygame.K_w]:
            if can_jump:
                player_y_velocity = jump_strength
                can_jump = False
            elif can_double_jump:
                player_y_velocity = jump_strength
                can_double_jump = False
        
        if key[pygame.K_LSHIFT] and key[pygame.K_w] and can_double_jump:
            player_y_velocity = jump_strength * 1.5  # Higher jump with double jump
            can_double_jump = False

        # Apply gravity
        player_y_velocity += gravity
        player.y += player_y_velocity

        # Collision with platforms
        on_ground = False
        for platform in platforms:
            if player.colliderect(platform):
                if player_y_velocity > 0:
                    player.bottom = platform.top
                    player_y_velocity = 0
                    can_jump = True
                    can_double_jump = True
                    on_ground = True
                break

        # Prevent the player from falling below the screen
        if player.bottom > SCREEN_HEIGHT:
            player.bottom = SCREEN_HEIGHT
            player_y_velocity = 0
            can_jump = True
            can_double_jump = True

        # Shooting projectiles
        if key[pygame.K_SPACE] and not space_pressed:
            projectile = Projectile(player.centerx + (player_size // 2 * player_direction), player.centery, projectile_speed, player_direction)
            player_projectiles.append(projectile)
            space_pressed = True
        elif not key[pygame.K_SPACE]:
            space_pressed = False

        # Update player projectiles
        for projectile in player_projectiles[:]:
            if not projectile.update():
                player_projectiles.remove(projectile)

        # Update enemies and check for shooting
        for enemy in enemies[:]:
            enemy.update(player.x)
            enemy_projectile = enemy.shoot(player.x, player.y)
            if enemy_projectile:
                enemy_projectiles.append(enemy_projectile)

        # Update enemy projectiles
        for projectile in enemy_projectiles[:]:
            if not projectile.update():
                enemy_projectiles.remove(projectile)
            elif player.colliderect(projectile.rect):
                # Player is hit by enemy bullet
                player_health -= 1
                enemy_projectiles.remove(projectile)
                if player_health <= 0:
                    game_active = False  # End game or show game over screen

        # Check collision between player projectiles and enemies
        for projectile in player_projectiles[:]:
            for enemy in enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    enemy.hit_count += 1
                    player_projectiles.remove(projectile)
                    if enemy.hit_count >= 3:
                        enemies.remove(enemy)
                    break

        # Draw the scrolling background
        screen.blit(background_image_2, (background_scroll, 0))
        screen.blit(background_image_2, (background_scroll + background_image_2_width, 0))

        # If background goes off the screen, reset
        if background_scroll <= -background_image_2_width:
            background_scroll = 0

        # Spawn new platforms if needed
        spawn_new_platforms()

        # Draw platforms
        for platform in platforms:
            screen.blit(platform_image, platform)

        # Draw coins
        for coin in coins[:]:
            screen.blit(Fire_coin, coin)
            if player.colliderect(coin):
                pygame.mixer.Sound.play(coin_sound)
                coins.remove(coin)
                score += 1

        # Draw the player
        pygame.draw.rect(screen, 'blue', player)

        # Draw projectiles
        for projectile in player_projectiles:
            projectile.draw(screen)
        for projectile in enemy_projectiles:
            projectile.draw(screen)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)

        # Draw health bar
        health_bar(screen, 10, 10, player_health, max_health)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and not game_active:
            if button.checkForInput(event.pos):
                game_active = True
                # Initialize platforms for the start of the game
                spawn_initial_platforms()

    pygame.display.update()
    pygame.time.Clock().tick(60)
