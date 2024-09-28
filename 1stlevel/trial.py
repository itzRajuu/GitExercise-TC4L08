import pygame
import sys
import random

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

# Background scrolling variables
background_scroll = 0
allow_left_scroll = False
scroll_limit = 600  # Limit after which the background starts scrolling
score = 0

# Load and scale the coin image
Fire_coin = pygame.image.load('fire_coin.png').convert_alpha()
Fire_coin = pygame.transform.smoothscale(Fire_coin, (90, 90))

# Load platform images
platform_image = pygame.image.load('platform_image.png').convert_alpha()
platform_image = pygame.transform.scale(platform_image, (200, 100))

# Initialize player variables
player_size = 200
player_x = 100
player_y = SCREEN_HEIGHT - player_size - 100
player_speed = 6
player_speed_y = 0
gravity = 0.5
jump_strength = -10
ground_level = SCREEN_HEIGHT - 100
max_jumps = 2
current_jumps = 0
player_direction = 1  # Direction the player is facing: 1 for right, -1 for left

# Player health
player_health = 3
max_health = 3

# Initialize player
player = pygame.Rect((player_x, player_y, player_size, player_size))
player_y_velocity = 0  # Vertical velocity for jumping
can_jump = True
can_double_jump = True

# Initialize score
score = 0

# Create a list to hold platform rects
platforms = []
platform_spawn_x = SCREEN_WIDTH  # Start spawning platforms from the right edge
platform_spawn_distance = 300  # Minimum distance between platform spawns
platform_spacing = 200  # Maximum vertical spacing between platforms
platform_timer = pygame.time.get_ticks()  # Start the timer
max_platforms_on_screen = 70  # Maximum number of platforms allowed on screen
platform_spawn_delay = 2000  # 1.5 seconds delay between each platform spawn
last_platform_spawn_time = pygame.time.get_ticks()  # Track last spawn time

# Create a list to hold coin rects
coins = []
coin_spawn_delay = 1500  # 1.5-second delay between each coin spawn
coin_timer = pygame.time.get_ticks()  # Start the timer

# Load images for character
character_standing = pygame.image.load("character/character_standing.png")
character_standing = pygame.transform.scale(character_standing, (player_size, player_size))
gif_forward = ["character/GameWalk1.png", "character/GameWalk2.png"]
video_frames_forward = [pygame.image.load(file).convert_alpha() for file in gif_forward]
video_frames_forward = [pygame.transform.scale(frame, (player_size, player_size)) for frame in video_frames_forward]
gif_backward = ["character/GameWalkLeft1.png", "character/GameWalkLeft2.png"]
video_frames_backward = [pygame.image.load(file).convert_alpha() for file in gif_backward]
video_frames_backward = [pygame.transform.scale(frame, (player_size, player_size)) for frame in video_frames_backward]

# Character movement and animation properties
character_rect = character_standing.get_rect(bottomleft=(player_x, player_y))
frame_index_forward = 0
frame_index_backward = 0
animation_speed = 5
time_per_frame = 1000 // animation_speed
is_moving_forward = False
is_moving_backward = False
last_frame_time_forward = pygame.time.get_ticks()
last_frame_time_backward = pygame.time.get_ticks()

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
enemy_spawn_delay = 5000  # 5 seconds delay between enemy spawns
last_enemy_spawn_time = pygame.time.get_ticks()

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, enemy_size, enemy_size)
        self.projectiles = []
        self.hit_count = 0

    def move(self):
        self.rect.x -= enemy_speed

    def shoot(self, player_x, player_y):
        if random.randint(1, enemy_shoot_interval) == 1:
            direction = -1 if player_x < self.rect.x else 1
            return Projectile(self.rect.centerx, self.rect.centery, enemy_projectile_speed, direction)
        return None

    def update(self, player_x):
        self.move()
        self.update_projectiles()
        if self.rect.right < 0:
            enemies.remove(self)  # Remove enemy if it goes off screen
        for projectile in self.projectiles[:]:
            if not projectile.update():
                self.projectiles.remove(projectile)

    def update_projectiles(self):
        for projectile in self.projectiles[:]:
            if not projectile.update():
                self.projectiles.remove(projectile)

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)  # Red for enemies
        for projectile in self.projectiles:
            projectile.draw(surface)

def spawn_initial_platforms():
    spawn_attempts = 0
    max_spawn_attempts = 10  # Limit the number of attempts to avoid infinite loops

    for _ in range(5):  # Spawn a few initial platforms
        while spawn_attempts < max_spawn_attempts:
            spawn_attempts += 1
            x = random.randint(SCREEN_WIDTH // 2, SCREEN_WIDTH - 200)
            y = SCREEN_HEIGHT - random.randint(100, 300)

            # Check distance from existing platforms
            too_close = False
            for platform in platforms:
                if abs(x - platform.x) < MIN_DISTANCE and abs(y - platform.y) < MIN_DISTANCE:
                    too_close = True
                    break
            
            if not too_close:
                create_platform(x, y)
                break  # Successfully spawned a platform, exit the loop

# Convert 2 cm to pixels (assuming 96 DPI)
MIN_DISTANCE = 76
# Track player movement start time
player_movement_start_time = None
movement_start_delay = 5000  # 5 seconds delay for starting platform spawning
platform_start_time = None  # Variable to track when to start spawning platforms

def spawn_new_platforms():
    global last_platform_spawn_time
    current_time = pygame.time.get_ticks()
    
    # Only spawn platforms if the player is moving horizontally
    if key[pygame.K_d] or key[pygame.K_a]:
        # Check if enough time has passed to spawn a new platform and the platform limit is not reached
        if current_time - last_platform_spawn_time >= platform_spawn_delay and len(platforms) < max_platforms_on_screen:
            x = SCREEN_WIDTH + random.randint(0, 300)  # Spawn platforms just outside the screen
            y = SCREEN_HEIGHT - random.randint(100, 300)

            # Check distance from existing platforms
            too_close = False
            for platform in platforms:
                if abs(x - platform.x) < MIN_DISTANCE and abs(y - platform.y) < MIN_DISTANCE:
                    too_close = True
                    break
            
            if not too_close:
                create_platform(x, y)
                last_platform_spawn_time = current_time

def create_platform(x, y):
    platform_width, platform_height = platform_image.get_size()
    platform_width -= 10  # Adjust width to be slightly smaller
    platform_height -= 10  # Adjust height to be slightly smaller
    platform_rect = pygame.Rect(x, y, platform_width, platform_height)
    platforms.append(platform_rect)
    # Optionally create a coin on the platform if needed


def is_near(player, coin, threshold=50):
    return (abs(player.centerx - coin.centerx) < threshold and
            abs(player.centery - coin.centery) < threshold)

def update_coin_spawn():
    global coin_timer
    current_time = pygame.time.get_ticks()

    if current_time - coin_timer >= coin_spawn_delay:
        x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300)
        y = SCREEN_HEIGHT - random.randint(100, 300)
        coin_rect = pygame.Rect(x, y, Fire_coin.get_width(), Fire_coin.get_height())
        coins.append(coin_rect)
        coin_timer = current_time

    # Coin collection check
    for coin in coins[:]:
        if is_near(player, coin):
            score += 10  # Increment score by 10 for each coin collected
            coins.remove(coin)
            coin_sound.play()  # Play the coin collection sound
        else:
            screen.blit(Fire_coin, (coin.x, coin.y))  # Draw the coin at its new position

def update_score_surface(surface, x, y, score):
    score_surface = main_font.render(f"Score: {score}", True, (255, 255, 255))  # White color
    surface.blit(score_surface, (x, y))

def health_bar(surface, x, y, current_health, max_health):
    bar_width = 200
    bar_height = 20
    fill = (current_health / max_health) * bar_width
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    
    pygame.draw.rect(surface, (255, 0, 0), outline_rect, 2)  # Red outline
    pygame.draw.rect(surface, (0, 255, 0), fill_rect)  # Green fill

def draw_game_over_screen():
    game_over_surface = main_font.render("Game Over", True, (255, 0, 0))
    screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - game_over_surface.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_surface.get_height() // 2))

class Projectile:
    def __init__(self, x, y, speed, direction):
        self.rect = pygame.Rect(x, y, 10, 5)
        self.speed = speed
        self.direction = direction
    
    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            return False
        return True

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 255), self.rect)  # Blue color for projectiles

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

# Main game loop
game_active = False
game_over = False
space_pressed = False

# Main game loop
game_active = False
game_over = False
space_pressed = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_active:
                if button.checkForInput(event.pos):
                    game_active = True  # Transition to the game screen

    screen.fill((0, 0, 0))  # Clear screen

    if game_over:
        draw_game_over_screen()
        pygame.display.update()
        pygame.time.wait(2000)  # Wait for 2 seconds to display the game over screen
        pygame.quit()
        sys.exit()

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
                if player_y_velocity > 0:  # Moving down
                    player.bottom = platform.top
                    player_y_velocity = 0
                    can_jump = True
                    can_double_jump = True
                    on_ground = True
                elif player_y_velocity < 0:  # Moving up
                    player.top = platform.bottom
                    player_y_velocity = 0
                break

        # Prevent the player from falling below the screen
        if player.bottom > SCREEN_HEIGHT:
            player.bottom = SCREEN_HEIGHT
            player_y_velocity = 0
            can_jump = True
            can_double_jump = True


        # Handle shooting projectiles
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

        # Draw the background
        screen.blit(background_image_2, (background_scroll, 0))
        screen.blit(background_image_2, (background_scroll + background_image_2_width, 0))

        # If background goes off the screen, reset
        if background_scroll <= -background_image_2_width:
            background_scroll = 0

        # Spawn new platforms and coins based on player movement
        spawn_new_platforms()
        update_coin_spawn()

        # Coin collection check
        for coin in coins[:]:
            if player.colliderect(coin):
                score += 10  # Increment score by 10 for each coin collected
                coins.remove(coin)
                coin_sound.play()  # Play the coin collection sound

        # Draw the platforms
        for platform in platforms:
            screen.blit(platform_image, platform)  # Platforms are drawn but not moved

        # Draw the coins
        for coin in coins:
            screen.blit(Fire_coin, (coin.x, coin.y))  # No need to adjust coin position here; it's already handled in update_coin_spawn

        # Draw the character animation
        current_time = pygame.time.get_ticks()
        if is_moving_forward:
            if current_time - last_frame_time_forward >= time_per_frame:
                frame_index_forward = (frame_index_forward + 1) % len(video_frames_forward)
                last_frame_time_forward = current_time
            screen.blit(video_frames_forward[frame_index_forward], player)
        elif is_moving_backward:
            if current_time - last_frame_time_backward >= time_per_frame:
                frame_index_backward = (frame_index_backward + 1) % len(video_frames_backward)
                last_frame_time_backward = current_time
            screen.blit(video_frames_backward[frame_index_backward], player)
        else:
            screen.blit(character_standing, player)

        # Draw projectiles
        for projectile in player_projectiles:
            projectile.draw(screen)
        for projectile in enemy_projectiles:
            projectile.draw(screen)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)

        # Draw health bar and score
        health_bar(screen, 10, 10, player_health, max_health)
        update_score_surface(screen, 10, 60, score)

        if game_over:
            draw_game_over_screen()
            game_active = False  # Stop the game loop when game over
            continue  # Skip the rest of the game loop

        # Spawn new enemies
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_spawn_time >= enemy_spawn_delay:
            x = SCREEN_WIDTH + 100
            y = SCREEN_HEIGHT - random.randint(100, 300)
            enemies.append(Enemy(x, y))
            last_enemy_spawn_time = current_time

    pygame.display.update()
    pygame.time.Clock().tick(60)