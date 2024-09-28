import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 50
COIN_SIZE = 30
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Collecting Game")

# Load player and coin images (or create simple rectangles)
player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
coins = []
for _ in range(10):
    x = random.randint(0, WIDTH - COIN_SIZE)
    y = random.randint(0, HEIGHT - COIN_SIZE)
    coins.append(pygame.Rect(x, y, COIN_SIZE, COIN_SIZE))

# Game variables
score = 0
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5
    if keys[pygame.K_UP]:
        player.y -= 5
    if keys[pygame.K_DOWN]:
        player.y += 5

    # Ensure the player stays on the screen
    player.x = max(0, min(player.x, WIDTH - PLAYER_SIZE))
    player.y = max(0, min(player.y, HEIGHT - PLAYER_SIZE))

    # Check for collisions with coins
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1

    # Drawing
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, player)
    for coin in coins:
        pygame.draw.rect(screen, YELLOW, coin)

    # Display score
    font = pygame.font.Font(None, 36)
    text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
