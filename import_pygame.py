import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BOARD_SIZE = (600, 600)
DICE_MIN, DICE_MAX = 1, 6
PLAYER_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
PLAYER_RADIUS = 15
START_POSITIONS = [(50, 550), (50, 50), (550, 50), (550, 550)]  # Corners of the board

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumanji Game")

# Load board image (Assuming you have a 'jumanji_board.png' image in the same directory)
board_image = pygame.image.load('jumanji_board.jpg')
board_image = pygame.transform.scale(board_image, BOARD_SIZE)

# Font setup
font = pygame.font.Font(None, 36)

# Game variables
num_players = 0
players = []
turn = 0

# Dice roll function
def roll_dice():
    return random.randint(DICE_MIN, DICE_MAX), random.randint(DICE_MIN, DICE_MAX)

# Main game loop
running = True
while running:
    screen.fill((0, 0, 0))  # Black background
    screen.blit(board_image, ((SCREEN_WIDTH - BOARD_SIZE[0]) // 2, (SCREEN_HEIGHT - BOARD_SIZE[1]) // 2))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and num_players == 0:
                num_players = 3  # Set number of players to 3 (as an example)
                for i in range(num_players):
                    players.append({"color": PLAYER_COLORS[i], "position": START_POSITIONS[i], "score": 0})
            elif event.key == pygame.K_SPACE and num_players > 0:
                dice1, dice2 = roll_dice()
                move = dice1 + dice2
                players[turn]["score"] += move  # Update the player's score
                # You could calculate the new position based on score or a predefined path here.
                turn = (turn + 1) % num_players  # Move to the next player's turn

    # Draw players
    for player in players:
        pygame.draw.circle(screen, player["color"], player["position"], PLAYER_RADIUS)

    # Display text
    if num_players == 0:
        text = font.render("Press Enter to start with 3 players.", True, (255, 255, 255))
    else:
        text = font.render(f"Player {turn + 1}'s turn! Press Space to roll the dice.", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()