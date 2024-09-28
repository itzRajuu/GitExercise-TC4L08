import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 800
HEIGHT = 600
PLAYER_SIZE = 50
PLAYER_SPEED = 5
GRAVITY = 1
JUMP_HEIGHT = 20

# Set up some variables
player_x = 100
player_y = 100
player_vx = 0
player_vy = 0

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load platform image
platform_image = pygame.image.load('platform.png')  # Replace 'platform.png' with your image file
platform_image = pygame.transform.scale(platform_image, (200, 50))  # Scale to match platform dimensions

# Set up platforms with positions and sizes
platforms = [
    {"x": 0, "y": HEIGHT - 50, "width": WIDTH, "height": 50},
    {"x": 300, "y": HEIGHT - 200, "width": 200, "height": 50},
    {"x": 600, "y": HEIGHT - 300, "width": 200, "height": 50}
]

# Set up the player
player = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)

# Game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player_vy == 0:
                player_vy = -JUMP_HEIGHT

    # Move the player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_vx = -PLAYER_SPEED
    elif keys[pygame.K_RIGHT]:
        player_vx = PLAYER_SPEED
    else:
        player_vx = 0

    player_x += player_vx
    player_y += player_vy

    # Apply gravity
    player_vy += GRAVITY

    # Check for collisions with platforms
    for platform in platforms:
        platform_rect = pygame.Rect(platform["x"], platform["y"], platform["width"], platform["height"])
        if player.colliderect(platform_rect):
            if player_vy > 0:  # Falling down
                player_y = platform["y"] - PLAYER_SIZE
                player_vy = 0
            elif player_vy < 0:  # Jumping up
                player_y = platform["y"] + platform["height"]
                player_vy = 0

    # Check if player is off the screen
    if player_y > HEIGHT:
        player_y = HEIGHT - PLAYER_SIZE
        player_vy = 0

    # Update player position
    player.x = player_x
    player.y = player_y

    # Draw everything
    screen.fill((255, 255, 255))
    for platform in platforms:
        screen.blit(platform_image, (platform["x"], platform["y"]))
    pygame.draw.rect(screen, (255, 0, 0), player)
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)
