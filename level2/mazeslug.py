import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 750
FPS = 60
TIMER_DURATION = 40  # Timer duration in seconds
HIDDEN_TRAP_DURATION = 5  # Duration before hidden trap appears

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Player settings
player_pos = [100, 600]
player_size = 50
player_velocity = 5
is_jumping = False
player_y_velocity = 0  # Player vertical velocity for smoother gravity
GRAVITY = 0.5  # Constant gravity force
on_ground = False  # Track if player is on ground
player_health = 100  # Initialize player health

# Load player sprite sheets
run_right_sprite_sheet = pygame.image.load('runright.png')
run_left_sprite_sheet = pygame.image.load('runleft.png')
jump_sprite_sheet = pygame.image.load('jump.png')

# Function to extract frames from a sprite sheet
def extract_frames(sheet, frame_width, frame_height, num_frames):
    frames = []
    for i in range(num_frames):
        frame_rect = (i * frame_width // num_frames, 0, frame_width // num_frames, frame_height)
        frames.append(sheet.subsurface(frame_rect))
    return frames

# Extract frames
run_right_frames = extract_frames(run_right_sprite_sheet, 332, 60, 6)
run_left_frames = extract_frames(run_left_sprite_sheet, 332, 60, 6)
jump_frames = extract_frames(jump_sprite_sheet, 311, 41, 6)

# Initialize animation variables
current_frame = 0
animation_timer = 0
animation_speed = 10  # Speed of the animation frames

# Maze layout with different platform types and traps
maze_layout = [
    "0000000000000000000000000",
    "1000000000000000000000001",
    "0110000000000000011111111",
    "0000000000000000000000001",
    "0000002000000011111100000",  # Added traps
    "0000111002000000111111111",
    "0001000111100000111111000",
    "000000000001110000000001",
    "1110000000001111111111111",
    "0000100110001111111111111",
    "0000000000000000000000000",
    "1111111111111111111111111",
]

# Platform images
platform_images = [
    pygame.image.load('iceplatform1.png'),
    pygame.image.load('iceplatform2.png'),
    pygame.image.load('iceplatform3.png'),
]

# Load the sprite sheet for traps
trap_sprite_sheet = pygame.image.load('watertrap_1.png')  # Your trap sprite sheet image
trap_frame_width = 200  # Width of the entire sprite sheet
trap_frame_height = 41   # Height of each trap frame
num_frames = 4  # Number of frames in the sprite sheet

# Function to extract a frame from the sprite sheet
def get_sprite(sheet, frame_rect):
    return sheet.subsurface(frame_rect)

# Create trap frames from the sprite sheet
trap_frames = []
for i in range(num_frames):
    frame_rect = (i * trap_frame_width // num_frames, 0, trap_frame_width // num_frames, trap_frame_height)
    trap_frames.append(get_sprite(trap_sprite_sheet, frame_rect))

# Resize platform images
platform_images = [pygame.transform.scale(img, (180, 40)) for img in platform_images]

# Create platforms and traps based on the maze layout
platforms = []
traps = []
gap_height = 40  # Height of the gap between platforms

for row_index, row in enumerate(maze_layout):
    for col_index, value in enumerate(row):
        if value == '1':
            platform_image_index = (row_index + col_index) % len(platform_images)
            platforms.append((pygame.Rect(col_index * 190, row_index * 60 + gap_height, 180, 40), platform_images[platform_image_index]))
        elif value == '2':
            traps.append(pygame.Rect(col_index * 190 + 75, row_index * 60 + gap_height, 40, 40))

# Load and scale background image
background = pygame.image.load('waterbg.jpg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Platformer")

# Initialize background position and offset
background_x = 0
offset_x = 0  # Initialize offset_x

# Timer setup
timer = TIMER_DURATION
font = pygame.font.Font(None, 36)  # Default font

# Hidden trap setup
hidden_trap_image = pygame.image.load('hidden_trap.gif')  # Load your hidden trap image
hidden_trap_image = pygame.transform.scale(hidden_trap_image, (40, 40))  # Resize if needed
hidden_trap_active = False
hidden_trap_timer = 0  # Timer for the hidden trap

# Set hidden trap position above a random platform
if platforms:
    random_platform = random.choice(platforms)
    platform_rect = random_platform[0]
    hidden_trap_pos = (platform_rect.centerx - 20, platform_rect.top - 40)  # Position the trap above the platform

# Platform movement variables
platform_movement_speed = 2  # Speed of the platform's movement
platform_moving_direction = 1  # 1 for down, -1 for up
platform_moving_index = 2  # Index of the platform to move (0-based index for the third platform)

# Main loop
clock = pygame.time.Clock()
frame_index = 0  # Animation frame index
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # Horizontal movement
    if keys[pygame.K_LEFT] and player_pos[0] > player_velocity:
        player_pos[0] -= player_velocity
        offset_x += player_velocity * 0.5  # Move platforms right
        current_frame += 1  # Animate running left
    elif keys[pygame.K_RIGHT] and player_pos[0] < SCREEN_WIDTH - player_size - player_velocity:
        player_pos[0] += player_velocity
        offset_x -= player_velocity * 0.5  # Move platforms left
        current_frame += 1  # Animate running right
    else:
        current_frame = 0  # Reset frame when not moving

    # Apply gravity
    player_y_velocity += GRAVITY  # Add gravity to vertical velocity
    player_pos[1] += player_y_velocity  # Update player position by velocity

    # Jump logic
    if not is_jumping and keys[pygame.K_SPACE] and on_ground:  # Only jump if on ground
        is_jumping = True
        player_y_velocity = -14  # Set the initial upward velocity for the jump
        on_ground = False  # Player is no longer on the ground

    # Handle jumping animation
    if is_jumping:
        current_frame += 1  # Animate jumping
    else:
        if keys[pygame.K_LEFT]:
            frame_index = current_frame // animation_speed % len(run_left_frames)
        elif keys[pygame.K_RIGHT]:
            frame_index = current_frame // animation_speed % len(run_right_frames)
        else:
            frame_index = 0  # Reset frame when not moving

    # Move the third platform up and down (only change its vertical position)
    if platforms:
        moving_platform = platforms[platform_moving_index][0]  # Get the Rect of the third platform
        # Update the vertical position of the moving platform
        moving_platform.y += platform_movement_speed * platform_moving_direction
        
        # Reverse direction if the platform reaches the limits
        if moving_platform.y <= (gap_height - 200):  # Up limit
            platform_moving_direction = 1  # Move down
        elif moving_platform.y >= 400:  # Down limit
            platform_moving_direction = -1  # Move up

    # Collision with platforms
    on_ground = False  # Reset on ground check for this frame
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)

    for platform_rect, platform_image in platforms:
        adjusted_platform_rect = platform_rect.move(offset_x, 0)
        
        # Only check collision with the top of the platform
        if player_rect.colliderect(adjusted_platform_rect):
            if player_y_velocity >= 0 and player_rect.bottom <= adjusted_platform_rect.top + 10:
                player_pos[1] = adjusted_platform_rect.top - player_size  # Correct player position
                player_y_velocity = 0  # Stop the player from falling
                is_jumping = False  # Reset jumping state
                on_ground = True  # Player is on the ground

    # Trap collision
    for trap_rect in traps:
        adjusted_trap_rect = trap_rect.move(offset_x, 0)
        
        # Adjust traps with offset
        if player_rect.colliderect(adjusted_trap_rect):
            player_health -= 10  # Lose health
            print(f"Health: {player_health}")  # Debug output
            player_pos = [100, 600]  # Reset player position

    # Update timer
    timer -= 1 / FPS  # Decrease timer by the frame time
    if timer <= 0:
        timer = 0
        # TODO: Trigger an event when time runs out, like ending the game or showing a message

    # Activate the hidden trap after HIDDEN_TRAP_DURATION seconds
    hidden_trap_timer += 1 / FPS  # Increase hidden trap timer
    if hidden_trap_timer >= HIDDEN_TRAP_DURATION:
        hidden_trap_active = True

    # Draw everything
    screen.fill(WHITE)
    screen.blit(background, (background_x, 0))

    # Draw platforms
    for platform_rect, platform_image in platforms:
        adjusted_platform_rect = platform_rect.move(offset_x, 0)
        screen.blit(platform_image, adjusted_platform_rect)

    # Draw traps
    for trap_rect in traps:
        adjusted_trap_rect = trap_rect.move(offset_x, 0)
        screen.blit(trap_frames[frame_index // 10 % num_frames], adjusted_trap_rect)  # Animate the traps

    # Draw the player with animations
    if is_jumping:
        frame_index = min(len(jump_frames) - 1, current_frame // animation_speed)
        screen.blit(jump_frames[frame_index], (player_pos[0], player_pos[1]))
    else:
        if keys[pygame.K_LEFT]:
            frame_index = current_frame // animation_speed % len(run_left_frames)
            screen.blit(run_left_frames[frame_index], (player_pos[0], player_pos[1]))
        elif keys[pygame.K_RIGHT]:
            frame_index = current_frame // animation_speed % len(run_right_frames)
            screen.blit(run_right_frames[frame_index], (player_pos[0], player_pos[1]))
        else:
            screen.blit(run_right_frames[0], (player_pos[0], player_pos[1]))  # Idle frame

    # Draw hidden trap (if active)
    if hidden_trap_active:
        screen.blit(hidden_trap_image, hidden_trap_pos)

    # Draw timer and health bar
    timer_text = font.render(f"Timer: {int(timer)}", True, WHITE)
    health_text = font.render(f"Health: {player_health}", True, RED)
    screen.blit(timer_text, (20, 20))
    screen.blit(health_text, (20, 50))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
