import pygame
import os

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("eli shane big")

# Load the animation frames
walk_frames = []
for i in range(1, 5):  # Assuming you have 4 walk frames (walk1.png to walk4.png)
   
    walk_frames.append(image)

# Animation variables
current_frame = 0
frame_rate = 5  # Number of frames per second
clock = pygame.time.Clock()

# Character position
x, y = 100, 300

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update animation frame
    current_frame += 1
    if current_frame >= len(walk_frames) * frame_rate:
        current_frame = 0

    # Display the current frame
    screen.fill((0, 0, 0))  # Fill the background with black
    frame_index = current_frame // frame_rate  # Control animation speed
    screen.blit(walk_frames[frame_index], (x, y))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(30)  # Run at 30 frames per second

# Quit Pygame
pygame.quit()
