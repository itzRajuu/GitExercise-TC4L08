import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 1000, 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Character Movement")

# Load background image
background_image = pygame.image.load("background.png")

# Load standing image
character_standing = pygame.image.load("character_standing.png")

# Load right key animation frames from PNG
gif_forward = ["GameWalk1.png", "GameWalk2.png",]  # List of PNG files
video_frames_forward = [pygame.image.load(file).convert_alpha() for file in gif_forward]

# Load left key animation frames from PNG
gif_backward = ["GameWalkLeft1.png", "GameWalkLeft2.png",]  # List of PNG files
video_frames_backward = [pygame.image.load(file).convert_alpha() for file in gif_backward]

# Character properties
character_rect = character_standing.get_rect(bottomleft=(0, screen_height - 50))  # Start from the far left bottom
velocity = 5
frame_index_forward = 0
frame_index_backward = 0
animation_speed = 7  # Number of frames per second for animation
time_per_frame = 1000 // animation_speed  # Time per frame in milliseconds

# Health bar properties
health = 100
health_bar_width = 200
health_bar_height = 20
health_bar_color = (255, 0, 0)  # Red
health_bar_background_color = (0, 0, 0)  # Black

# Main loop
running = True
is_moving_forward = False
is_moving_backward = False
clock = pygame.time.Clock()
last_frame_time_forward = pygame.time.get_ticks()  # Initialize time tracker for forward movement
last_frame_time_backward = pygame.time.get_ticks()  # Initialize time tracker for backward movement

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
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

    # Draw background image
    screen.blit(background_image, (0, 0))

    # Check if moving forward and update animation frames
    if is_moving_forward:
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time_forward > time_per_frame:
            frame_index_forward = (frame_index_forward + 1) % len(video_frames_forward)  # Loop through frames
            last_frame_time_forward = current_time
        screen.blit(video_frames_forward[frame_index_forward], character_rect)
        character_rect.x += velocity
    # Check if moving backward and update animation frames
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

    # Draw health bar
    health_bar_rect = pygame.Rect(10, 10, health_bar_width, health_bar_height)
    pygame.draw.rect(screen, health_bar_background_color, health_bar_rect)
    health_bar_fill_width = int(health_bar_width * (health / 100))
    pygame.draw.rect(screen, health_bar_color, (10, 10, health_bar_fill_width, health_bar_height))

    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Quit
pygame.quit()