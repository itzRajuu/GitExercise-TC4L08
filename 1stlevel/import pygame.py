import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Initialize clock
clock = pygame.time.Clock()

# Load the starting song
pygame.mixer.music.load('Title_song-1.mp3')
pygame.mixer.music.play(loops=-1)

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 750
FPS = 60
  # Timer duration in seconds
HIDDEN_TRAP_DURATION = 5  # Duration before hidden trap appears


# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)



screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slugterra Game")
main_font = pygame.font.SysFont("cambria", 50)

# Player settings
player_pos = [100, 600]
player_size = 50
player_velocity = 3
is_jumping = False
player_y_velocity = 0  # Player vertical velocity for smoother gravity
GRAVITY = 0.5  # Constant gravity force
on_ground = False  # Track if player is on ground
player_health = 100  # Initialize player health
player_score = 0  # Initialize player score

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

# Bullet settings
bullets = []
bullet_velocity = 10
enemy_bullets = []
bullet_type = 0  # 0 for normal bullet, 1 for special bullet

# Load bullet images
player_bullet_image = pygame.image.load('fire_bullet1.png')
player_bullet_image = pygame.transform.scale(player_bullet_image, (30, 20))
player_special_bullet_image = pygame.image.load('joules2.png')
player_special_bullet_image = pygame.transform.scale(player_special_bullet_image, (30, 20))
enemy_bullet_image = pygame.image.load('enemy_bullet.png')
enemy_bullet_image = pygame.transform.scale(enemy_bullet_image, (30, 20))

# Maze layout with different platform types and traps
maze_layout = [
    "0000000000000000000000000",
    "1000000000000000000000001",
    "0110000000000000011111111",
    "00000000000000020D0000001",
    "0000002000000011111100000",  # Added traps
    "0000111000000000000000111",
    "0001000111100000111111000", #
    "0000000000011100000000001",
    "1110000000000010000110000",
    "0000100110001110000000111",
    "0000000000000000000000000",
    "1111111111111111111111111",  # Door at the end
]

# Platform images
platform_images = [
    pygame.image.load('platform_image.png'),
    pygame.image.load('platform_image.png'),
    pygame.image.load('platform_image.png'),
]

# Load the sprite sheet for traps
trap_image = pygame.image.load('trap_image.jpg')  # Your trap sprite sheet image
trap_image = pygame.transform.scale(trap_image, (40, 40))  # Resize if needed


# Function to extract a frame from the sprite sheet
def get_sprite(sheet, frame_rect):
    return sheet.subsurface(frame_rect)



# Resize platform images
platform_images = [pygame.transform.scale(img, (180, 40)) for img in platform_images]

# Load door image
door_image = pygame.image.load('door.png')
door_image = pygame.transform.scale(door_image, (180, 40))

# Load coin image
coin_image = pygame.image.load('fire_coin.png')  # Replace 'coin.png' with your actual coin image file
coin_image = pygame.transform.scale(coin_image, (50, 50))  # Resize as needed
# Load coin collection sound
coin_sound = pygame.mixer.Sound('coin_sound.mp3')  # Replace 'coin_collect.wav' with your actual sound file

# Create platforms and traps based on the maze layout
platforms = []
traps = []
doors = []
gap_height = 40 # Height of the gap between platforms
coins = []

# Load special object image
special_object_image = pygame.image.load('waterelemental.png')
special_object_image = pygame.transform.scale(special_object_image, (40, 40))  # Resize if needed

for row_index, row in enumerate(maze_layout):
    for col_index, value in enumerate(row):
        if value == '1':
            platform_image_index = (row_index + col_index) % len(platform_images)
            platforms.append((pygame.Rect(col_index * 190, row_index * 60 + gap_height, 180, 40), platform_images[platform_image_index]))
            if random.random() < 0.5:  # 50% chance of a coin on the platform
                coin_pos = (col_index * 190 + 90, row_index * 60 + gap_height - 20)  # Define coin_pos here
                coins.append(coin_pos)
        elif value == '2':
            traps.append(pygame.Rect(col_index * 190 + 75, row_index * 60 + gap_height, 40, 40))
        elif value == 'D':
            doors.append(pygame.Rect(col_index * 190, row_index * 60 + gap_height, 180, 40))

# Set special object position before the last platform
if platforms:
    last_platform = platforms[-1]
    platform_rect = last_platform[0]
    special_object_pos = (platform_rect.centerx - 20, platform_rect.top - 60)  # Position the object before the last platform# Load and scale background image
background = pygame.image.load('earth_elemental.jpg')
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption (" Maze Platformer")

# Initialize background position and offset
background_x = 0
offset_x = 0  # Initialize offset_x



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

# Enemy settings
enemy_pos = [800, 500]
enemy_size = 50
enemy_velocity = 2
enemy_health = 70
enemy_on_ground = False  # Track if enemy is on ground
enemy_y_velocity = 0  # Enemy vertical velocity for smoother gravity
enemy_shoot_cooldown = 0  # Cooldown for enemy shooting
enemy_alive = True  # Track if enemy is alive

# Load enemy image
enemy_image = pygame.image.load('enemi.png')  # Replace 'enemy.png' with your actual enemy image file
enemy_image = pygame.transform.scale(enemy_image, (50, 50))  # Resize the image to match the enemy size

# Main loop
clock = pygame.time.Clock()
frame_index = 0  # Animation frame index
game_over = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                bullet_type = 1 - bullet_type  # Toggle between 0 and 1

    if not game_over:
        keys = pygame.key.get_pressed()

        offset_speed = 2.0

        # Horizontal movement
        if keys[pygame.K_a] and player_pos[0] > player_velocity:
            player_pos[0] -= player_velocity
            offset_x += player_velocity * offset_speed  # Move platforms right
            current_frame += 1  # Animate running left
        elif keys[pygame.K_d] and player_pos[0] < SCREEN_WIDTH - player_size - player_velocity:
            player_pos[0] += player_velocity
            offset_x -= player_velocity * offset_speed  # Move platforms left
            current_frame += 1  # Animate running right
        else:
            current_frame = 0  # Reset frame when not moving

        # Apply gravity
        player_y_velocity += GRAVITY  # Add gravity to vertical velocity
        player_pos[1] += player_y_velocity  # Update player position by velocity

        # Jump logic
        if not is_jumping and keys[pygame.K_w] and on_ground:  # Only jump if on ground
            is_jumping = True
            player_y_velocity = -14  # Set the initial upward velocity for the jump
            on_ground = False  # Player is no longer on the ground

        # Shooting logic
        if keys[pygame.K_SPACE] and not bullets:
            if bullet_type == 0:
                bullet_rect = pygame.Rect(player_pos[0] + player_size // 2 - 5, player_pos[1] + 20, 10, 5)
                bullets.append((bullet_rect, player_bullet_image))
            else:
                bullet_rect = pygame.Rect(player_pos[0] + player_size // 2 - 10 , player_pos[1] + 20, 20, 10)
                bullets.append((bullet_rect, player_special_bullet_image))

        # Update bullets
        for bullet in bullets[:]:
            bullet[0].x += bullet_velocity  # Move bullet to the right

            # Check collision with enemy
            enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)
            if bullet[0].colliderect(enemy_rect) and enemy_alive:
                enemy_health -= 10  # Reduce enemy health
                print(f"Enemy Health: {enemy_health }")  # Debug output
                bullets.remove(bullet)  # Remove the bullet

                # Check if enemy is dead
                if enemy_health <= 0:
                    enemy_alive = False

        # Handle jumping animation
        if is_jumping:
            current_frame += 1  # Animate jumping
        else:
            if keys[pygame.K_a]:
                frame_index = current_frame // animation_speed % len(run_left_frames)
            elif keys[pygame.K_d]:
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
                    player_y_velocity = 0  # Reset vertical velocity
                    is_jumping = False  # Reset jumping state
                    on_ground = True  # Player is on the ground

        # Collision with doors
        for door_rect in doors:
            adjusted_door_rect = door_rect.move(offset_x, 0)
            
            if player_rect.colliderect(adjusted_door_rect):
                game_over = True  # Game ends when player reaches the door

        if on_ground:
            player_y_velocity = 0

        # Trap collision
        for trap_rect in traps:
            adjusted_trap_rect = trap_rect.move(offset_x, 0)
            
            # Adjust traps with offset
            if player_rect.colliderect(adjusted_trap_rect):
                player_health -= 10  # Lose health
                print(f"Health: {player_health}")  # Debug output
                if player_health <= 0:
                    game_over = True

        # Coin collection
        for coin_pos in coins[:]:
            adjusted_coin_pos = (coin_pos[0] + offset_x, coin_pos[1])
            if player_rect.collidepoint(adjusted_coin_pos):
                player_score += 1  # Increase player score
                print(f"Score: {player_score}")  # Debug output
                coin_sound.play()  # Play the coin collection sound
                coins.remove(coin_pos)  # Remove the coin

        # Special object collection
        special_object_rect = pygame.Rect(special_object_pos[ 0], special_object_pos[1], 40, 40)
        if player_rect.colliderect(special_object_rect):
            player_score += 10  # Increase player score
            print(f"Score: {player_score}")  # Debug output
            special_object_pos = (-100, -100)  # Move the object off-screen

        # Enemy movement
        if enemy_pos[0] < player_pos[0] and enemy_alive:
            enemy_pos[0] += enemy_velocity
        elif enemy_pos[0] > player_pos[0] and enemy_alive:
            enemy_pos[0] -= enemy_velocity

        # Apply gravity to enemy
        enemy_y_velocity += GRAVITY  # Add gravity to vertical velocity
        enemy_pos[1] += enemy_y_velocity  # Update enemy position by velocity

        # Enemy collision with platforms
        # Enemy collision with platforms
        enemy_on_ground = False  # Reset on ground check for this frame
        enemy_rect = pygame.Rect(enemy_pos[0], enemy_pos[1], enemy_size, enemy_size)

        for platform_rect, platform_image in platforms:
            adjusted_platform_rect = platform_rect.move(offset_x, 0)
            
            # Only check collision with the top of the platform
            if enemy_rect.colliderect(adjusted_platform_rect):
                if enemy_y_velocity >= 0 and enemy_rect.bottom <= adjusted_platform_rect.top + 10:
                    enemy_pos[1] = adjusted_platform_rect.top - enemy_size  # Correct enemy position
                    enemy_y_velocity = 0  # Stop the enemy from falling
                    enemy_on_ground = True  # Enemy is on the ground
        # Enemy shooting
        enemy_shoot_cooldown -= 1 / FPS
        if enemy_shoot_cooldown <= 0 and enemy_alive:
            enemy_shoot_cooldown = 1  # Reset cooldown
            enemy_bullet_rect = pygame.Rect(enemy_pos[0] + enemy_size // 2 - 5, enemy_pos[1] + 20, 10, 5)
            enemy_bullets.append((enemy_bullet_rect, enemy_bullet_image))

        # Update enemy bullets
# Update enemy bullets
        for enemy_bullet in enemy_bullets[:]:
            enemy_bullet[0].x -= bullet_velocity  # Move bullet to the left

            # Check collision with player
            player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)
            if enemy_bullet[0].colliderect(player_rect):
                player_health -= 10  # Reduce player health
                print(f"Health: {player_health}")  # Debug output
                enemy_bullets.remove(enemy_bullet)  # Remove the bullet

        # Check if player is dead
        if player_health <= 0:
            game_over = True        # Enemy collision
        if player_rect.colliderect(enemy_rect) and enemy_alive:
            player_health -= 10  # Lose health
            print(f"Health: {player_health}")  # Debug output
            if player_health <= 0:
                game_over = True

        # Update timer
       # timer -= 1 / FPS  # Decrease timer by the frame time
        #if timer <= 0:
         #   timer = 0
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
        # Draw traps
    for trap_rect in traps:
        adjusted_trap_rect = trap_rect.move(offset_x, 0)
        screen.blit(trap_image, adjusted_trap_rect)  # Draw the trap image
    # Draw doors
    for door_rect in doors:
        adjusted_door_rect = door_rect.move(offset_x, 0)
        screen.blit(door_image, adjusted_door_rect)

    # Draw coins
        # Draw coins
    for coin_pos in coins:
        adjusted_coin_pos = (coin_pos[0] + offset_x, coin_pos[1])
        screen.blit(coin_image, adjusted_coin_pos)  # Draw the coin image


    # Draw special object
    screen.blit(special_object_image, special_object_pos)

    # Draw the player with animations
    if not game_over:
        if is_jumping:
            frame_index = min(len(jump_frames) - 1, current_frame // animation_speed)
            screen.blit(jump_frames[frame_index], (player_pos[0], player_pos[1]))
        else :
            if keys[pygame.K_a]:
                frame_index = current_frame // animation_speed % len(run_left_frames)
                screen.blit(run_left_frames[frame_index], (player_pos[0], player_pos[1]))
            elif keys[pygame.K_d]:
                frame_index = current_frame // animation_speed % len(run_right_frames)
                screen.blit(run_right_frames[frame_index], (player_pos[0], player_pos[1]))
            else:
                screen.blit(run_right_frames[0], (player_pos[0], player_pos[1]))  # Idle frame

    # Draw bullets
    for bullet in bullets:
        screen.blit(bullet[1], (bullet[0].x, bullet[0].y))  # Draw the bullet

    # Draw enemy bullets
    for enemy_bullet in enemy_bullets:
        screen.blit(enemy_bullet[1], (enemy_bullet[0].x, enemy_bullet[0].y))  # Draw the enemy bullet

    # Draw hidden trap (if active)
    if hidden_trap_active:
        screen.blit(hidden_trap_image, hidden_trap_pos)

    # Draw enemy
    if enemy_alive:
        screen.blit(enemy_image, (enemy_pos[0], enemy_pos[1]))  # Draw the enemy image

    # Draw enemy health bar
    if enemy_alive:
        enemy_health_bar_width = 50
        enemy_health_bar_height = 10
        enemy_health_bar_x = enemy_pos[0] + enemy_size // 2 - enemy_health_bar_width // 2
        enemy_health_bar_y = enemy_pos[1] - enemy_health_bar_height - 5
        pygame.draw.rect(screen, RED, (enemy_health_bar_x, enemy_health_bar_y, enemy_health_bar_width, enemy_health_bar_height))
        pygame.draw.rect(screen, GREEN, (enemy_health_bar_x, enemy_health_bar_y, enemy_health_bar_width * enemy_health // 50, enemy_health_bar_height))

    # Draw enemy death text
    if not enemy_alive:
        enemy_death_text = font.render("Enemy Defeated!", True, RED)
        screen.blit(enemy_death_text, (enemy_pos[0], enemy_pos[1] - 20))

    # Draw player health bar
    player_health_bar_width = 50
    player_health_bar_height = 10
    player_health_bar_x = player_pos[0] + player_size // 2 - player_health_bar_width // 2
    player_health_bar_y = player_pos[1] - player_health_bar_height - 5
    pygame.draw.rect(screen, RED, (player_health_bar_x, player_health_bar_y, player_health_bar_width, player_health_bar_height))
    pygame.draw.rect(screen, GREEN, (player_health_bar_x, player_health_bar_y, player_health_bar_width * player_health // 100, player_health_bar_height))

    # Draw timer and health text
   
    health_text = font.render(f"Health: {player_health}", True, RED)
    score_text = font.render(f"Score: {player_score}", True, YELLOW)
  
    screen.blit(health_text, (20, 50))
    screen.blit(score_text, (20, 80))

    # Draw game over text
# Draw game over text
    if game_over:
        screen.fill(WHITE)  # Fill the screen with white
        
        if player_health <= 0:
            died_text = font.render("YOU DIED NOOBIE WOHOHOHOHOH", True, RED)
            screen.blit(died_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 25))  # Center the died message
        else:
            game_over_text = font.render("ELEMENTAL IS COLLECTED MATE, LETS GOOOO", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 25))  # Center the win text

        pygame.display.flip()  # Update the display
        pygame.time.wait(2000)  # Wait for 2 seconds before exiting
        break  # Exit the game loop
    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)