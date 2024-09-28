import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Load the starting song
pygame.mixer.music.load('Title_song-1.mp3')
pygame.mixer.music.play(loops=-1)

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slugterra Game")
main_font = pygame.font.SysFont("cambria", 50)

# Colors
PLATFORM_COLOR = (100, 50, 150)  # Define platform color for the platform image
PLATFORM_RECT_COLOR = (255, 0, 0)  # Color for the collision debug rectangle
HEALTH_BAR_COLOR = (0, 255, 0)  # Green health bar
ENEMY_COLOR = (255, 0, 0)  # Red for the enemy
ENEMY_HEALTH_BAR_COLOR = (255, 0, 0)  # Red for the enemy health bar
ENEMY_BULLET_COLOR = (255, 0, 0)  # Red for enemy bullets
COIN_COLOR = (255, 255, 0)  # Yellow for the coins

# Load background images
background_image = pygame.image.load('Slug.Background.jpg')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_image_2 = pygame.image.load('Earth_elemental.jpg')
background_image_2 = pygame.transform.scale(background_image_2, (SCREEN_WIDTH * 2, SCREEN_HEIGHT))
background_image_2_width = background_image_2.get_width()

# Initialize background scrolling variables
background_scroll = 0
scroll_speed = 3

# Load and scale the coin image
Fire_coin = pygame.image.load('fire_coin.png').convert_alpha()
Fire_coin = pygame.transform.smoothscale(Fire_coin, (90, 90))

# Load and scale the platform image
platform_width = 150
platform_height = 30
platform_image = pygame.image.load('platform_image.png').convert_alpha()
platform_image = pygame.transform.scale(platform_image, (platform_width, platform_height))

# Load and scale the bullet image
bullet_width = 50  # Increased width
bullet_height = 30  # Increased height
bullet_image = pygame.image.load('fire_bullet1.png').convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (bullet_width, bullet_height))

# Initialize player variables
player_width = 80
player_height = 40
player_x = 100
player_y = SCREEN_HEIGHT - player_height - 100
player_speed = 5
player_y_velocity = 0
gravity = 1.0
jump = -15
max_jumps = 2
current_jumps = 0
player_health = 100

# Initialize player
player = pygame.Rect((player_x, player_y, player_width, player_height))
can_jump = True
can_double_jump = True

# Platform settings
platform_gap = 300
platform_step_height = 50
initial_platform_y = SCREEN_HEIGHT - 120
platforms = []

# Coin settings
coin_size = 30
coins = []

# Enemy settings
enemy_width = 50
enemy_height = 50
enemy_speed = 2
enemy_health = 4
enemy = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT - player_height - 50, enemy_width, enemy_height)
enemy_bullets = []
enemy_last_shot_time = 0
enemy_shooting_interval = 2000

# Bullet settings
bullet_speed = 10
bullets = []
space_pressed = False  # Flag to track if spacebar was pressed

# Function to create platforms in a step-like pattern
def create_platforms_and_coins():
    for i in range(5):
        x = 200 + i * 300  # Spacing between platforms
        y = initial_platform_y - i * 100  # Height of each platform
        platforms.append(pygame.Rect(x, y, platform_width, platform_height))
        
        # Create a coin above each platform
        coin_x = x + (platform_width - coin_size) // 2  # Center the coin
        coin_y = y - coin_size - 10  # Position the coin above the platform
        coins.append(pygame.Rect(coin_x, coin_y, coin_size, coin_size))


# Function to create coins above platforms

# Load images for character
def load_sprite_sheet(filename, frame_width, frame_height):
    sprite_sheet = pygame.image.load(filename).convert_alpha()
    frames = []
    for i in range(sprite_sheet.get_width() // frame_width):
        frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames

run_sprites = load_sprite_sheet('Character/run1.png', 37, 40)  
jump_sprites = load_sprite_sheet('Character/jump1.png', 45, 32)  
run_back_sprites = load_sprite_sheet('Character/run_back1.png', 37, 40)  
idle_sprites = load_sprite_sheet('Character/idle1.png', 37, 43)  

# Animation settings
current_frame = 0
frame_counts = {
    'run': len(run_sprites),
    'jump': len(jump_sprites),
    'run_back': len(run_back_sprites),
    'idle': len(idle_sprites)
}

action = 'idle'  # Initial action
clock = pygame.time.Clock()

# Main game function
def main_game():
    global player_y_velocity, current_frame, background_scroll, current_jumps, can_jump, can_double_jump, bullets, player_health, enemy, enemy_bullets, enemy_last_shot_time, enemy_health, space_pressed

    # Spawn step platforms
    create_platform()
      # Create coins above platforms

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # Adjust background scrolling based on player movement (opposite direction)
        if keys[pygame.K_d]:  # Move right
            player.x += player_speed
            background_scroll -= player_speed  # Scroll background to the left
            for platform in platforms:
                platform.x -= player_speed  # Move platforms left with the background
            action = 'run'
        elif keys[pygame.K_a]:  # Move left
            player.x -= player_speed
            background_scroll += player_speed  # Scroll background to the right
            for platform in platforms:
                platform.x += player_speed  # Move platforms right with the background
            action = 'run_back'
        else:
            action = 'idle'

        # Jumping logic
        if keys[pygame.K_w]:
            if can_jump:  # First jump
                player_y_velocity = jump
                can_jump = False
                current_jumps = 1
                action = 'jump'
            elif can_double_jump and current_jumps < max_jumps:  # Double jump
                player_y_velocity = jump
                can_double_jump = False
                current_jumps += 1
                action = 'jump'

        # Shooting logic (press space to shoot)
        if keys[pygame.K_SPACE]:
            if not space_pressed:  # Only fire if spacebar was not pressed previously
                # Create a new bullet
                bullet = pygame.Rect(player.right, player.y + player_height // 2 - bullet_height // 2, bullet_width, bullet_height)
                bullets.append(bullet)
                space_pressed = True
        else:
            space_pressed = False  # Reset flag when spacebar is released

        # Apply gravity
        player_y_velocity += gravity
        player.y += player_y_velocity

        # Collision with platforms (only if moving downward)
        on_ground = False
        for platform in platforms:
            if player.colliderect(platform) and player_y_velocity > 0:
                player.bottom = platform.top  # Align player's bottom to platform's top
                player_y_velocity = 0
                can_jump = True
                can_double_jump = True
                current_jumps = 0
                on_ground = True
                break  # Exit the loop as we are now standing on a platform

        # Prevent the player from "climbing" when not falling
        if not on_ground and player.bottom < SCREEN_HEIGHT:
            player_y_velocity += gravity  # Apply gravity when not grounded

        # Ensure the player doesn't fall off the screen
        if player.bottom > SCREEN_HEIGHT:
            player.bottom = SCREEN_HEIGHT
            player_y_velocity = 0
            can_jump = True
            can_double_jump = True
            current_jumps = 0

        # Move bullets
        for bullet in bullets:
            bullet.x += bullet_speed

        # Remove bullets that go off-screen
        bullets = [bullet for bullet in bullets if bullet.x < SCREEN_WIDTH]

        # Enemy shooting logic
        current_time = pygame.time.get_ticks()
        if current_time - enemy_last_shot_time > enemy_shooting_interval:
             enemy_last_shot_time = current_time
             enemy_bullet = pygame.Rect(enemy.left - bullet_width, enemy.y + enemy_height // 2 - bullet_height // 2, bullet_width, bullet_height)
             enemy_bullets.append(enemy_bullet)

        # Move enemy bullets
        for enemy_bullet in enemy_bullets:
            enemy_bullet.x -= bullet_speed

        # Remove enemy bullets that go off-screen
        enemy_bullets = [enemy_bullet for enemy_bullet in enemy_bullets if enemy_bullet.x > 0]

        # Check for collision between player and enemy bullets
        for enemy_bullet in enemy_bullets:
            if player.colliderect(enemy_bullet):
                player_health -= 1  # Reduce player's health when hit by an enemy bullet
                enemy_bullets.remove(enemy_bullet)  # Remove the bullet after collision

        # Check for collision between bullets and enemy
        for bullet in bullets:
            if enemy.colliderect(bullet):
                enemy_health -= 1  # Reduce enemy health when hit by a bullet
                bullets.remove(bullet)  # Remove the bullet after collision
                if enemy_health <= 0:
                    enemy = pygame.Rect(-100, -100, enemy_width, enemy_height)  # Move enemy off-screen

        # Check for coin collection
        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)  # Remove the coin if collected

        # Draw background
        screen.fill((255, 255, 255))
        screen.blit(background_image_2, (background_scroll, 0))
        screen.blit(background_image_2, (background_scroll - background_image_2_width, 0))

        # Draw the current frame of the action
        if action == 'run':
            screen.blit(run_sprites[current_frame], (player.x, player.y))
        elif action == 'jump':
            screen.blit(jump_sprites[current_frame], (player.x, player.y))
        elif action == 'run_back':
            screen.blit(run_back_sprites[current_frame], (player.x, player.y))
        elif action == 'idle':
            screen.blit(idle_sprites[current_frame], (player.x, player.y))

        # Draw bullets
        for bullet in bullets:
            screen.blit(bullet_image, bullet.topleft)  # Draw the bullet image at the bullet's position

        # Draw enemy bullets
        for enemy_bullet in enemy_bullets:
            pygame.draw.rect(screen, ENEMY_BULLET_COLOR, enemy_bullet)  # Draw enemy bullets in red

        # Draw platforms
        for platform in platforms:
            # Draw the platform image
            screen.blit(platform_image, (platform.x, platform.y))  # Draw the platform image at the rectangle’s position

        # Draw coins
        for coin in coins:
            pygame.draw.rect(screen, COIN_COLOR, coin)  # Draw the coin

        # Draw the enemy
        if enemy.x >= 0:  # Draw the enemy only if it is on-screen
            pygame.draw.rect(screen, ENEMY_COLOR, enemy)  # Draw the enemy in red
            
            # Draw the enemy's health bar
            health_bar_width = 50
            health_bar_height = 5
            pygame.draw.rect(screen, (0, 0, 0), (enemy.x, enemy.y - 15, health_bar_width, health_bar_height))  # Background of the health bar
            pygame.draw.rect(screen, ENEMY_HEALTH_BAR_COLOR, (enemy.x, enemy.y - 15, (enemy_health / 4) * health_bar_width, health_bar_height))  # Foreground of the health bar

        # Draw the player's health bar
        health_bar_width = 200
        health_bar_height = 20
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, health_bar_width, health_bar_height))  # Background of the health bar
        pygame.draw.rect(screen, HEALTH_BAR_COLOR, (10, 10, (player_health / 100) * health_bar_width, health_bar_height))  # Foreground of the health bar

        # Update the display
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main_game()

