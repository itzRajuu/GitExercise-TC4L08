import pygame
from moviepy.editor import VideoFileClip

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 1000, 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Character Movement")

# Load standing image
character_standing = pygame.image.load("character_standing.png")

# Load MP4 animation without resizing
clip = VideoFileClip("GameWalk.mp4")

# Extract video frames with the correct size
video_frames = []
for frame in clip.iter_frames():
    frame_surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
    video_frames.append(frame_surface)

# Character properties
character_rect = character_standing.get_rect(bottomleft=(0, screen_height - 50))  # Start from the far left bottom
velocity = 5
frame_index = 0
animation_speed = 10  # Number of frames per second for animation
time_per_frame = 1000 // animation_speed  # Time per frame in milliseconds

# Main loop
running = True
is_moving = False
clock = pygame.time.Clock()
last_frame_time = pygame.time.get_ticks()  # Initialize time tracker

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                is_moving = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                is_moving = False

    # Clear screen
    screen.fill((255, 255, 255))

    # Check if moving and update animation frames
    if is_moving:
        current_time = pygame.time.get_ticks()
        if current_time - last_frame_time > time_per_frame:
            frame_index = (frame_index + 1) % len(video_frames)  # Loop through frames
            last_frame_time = current_time
        screen.blit(video_frames[frame_index], character_rect)
        character_rect.x += velocity
    else:
        # If not moving, show the standing image
        screen.blit(character_standing, character_rect)

    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Quit
pygame.quit()