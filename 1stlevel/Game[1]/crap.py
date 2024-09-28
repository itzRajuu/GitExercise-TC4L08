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

# Initialize background scrolling variables
background_scroll = 0
scroll_limit = 5  # Limit after which the background starts scrolling

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
player_speed = 3
player_speed_y = 0
gravity = 0.5
jump = -10
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
platform_spawn_distance = 500  # Minimum distance between platform spawns
platform_spacing = 300  # Maximum vertical spacing between platforms
platform_timer = pygame.time.get_ticks()  # Start the timer
max_platforms_on_screen = 70  # Maximum number of platforms allowed on screen
platform_spawn_delay = 1500  # 1.5 seconds delay between each platform spawn

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
velocity = 3
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

class Projectile:
    def __init__(self, x, y, speed, direction):
        self.rect = pygame.Rect(x, y, 10, 5)
        self.speed = speed
        self.direction = direction
        self.color = (255, 0, 0)  # Red color for the projectile

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH:
            return False
        return True

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Enemy settings
enemy_size = 50
enemies = []
enemy_projectile_speed = 7
enemy_shoot_interval = 60  # Adjust shooting speed
enemy_speed = 1
enemy_gravity = 0.5

# Platform spawning logic
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
    global last_platform_spawn_time, player_movement_start_time, platform_start_time
    current_time = pygame.time.get_ticks()
    
    # Start the movement timer when the player starts moving
    if player_movement_start_time is None and (key[pygame.K_d] or key[pygame.K_a]):
        player_movement_start_time = current_time

    # Check if 10 seconds have passed since the game became active
    if platform_start_time is None:
        if current_time - platform_timer >= 10000:  # 10 seconds delay before spawning starts
            platform_start_time = current_time

    # If 5 seconds have passed since player started moving
    if player_movement_start_time and (current_time - player_movement_start_time >= movement_start_delay):
        # Check if enough time has passed to spawn a new platform and the platform limit is not reached
        if current_time - last_platform_spawn_time >= platform_spawn_delay and len(platforms) < max_platforms_on_screen:
            x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300)
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
    platform_rect = pygame.Rect(x, y, platform_image.get_width(), platform_image.get_height())
    platforms.append(platform_rect)

def update_coin_spawn():
    global coin_timer
    current_time = pygame.time.get_ticks()

    if current_time - coin_timer >= coin_spawn_delay:
        x = random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300)
        y = SCREEN_HEIGHT - random.randint(100, 300)
        coin_rect = pygame.Rect(x, y, Fire_coin.get_width(), Fire_coin.get_height())
        coins.append(coin_rect)
        coin_timer = current_time

def update_score_surface(surface, x, y, score):
    score_surface = main_font.render(f"Score: {score}", True, (255, 255, 255))
    surface.blit(score_surface, (x, y))

def health_bar(surface, x, y, health, max_health):
    bar_length = 200
    bar_height = 20
    fill = (health / max_health) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, (255, 0, 0), outline_rect, 2)
    pygame.draw.rect(surface, (0, 255, 0), fill_rect)

# Define the Button class with text
class Button:
    def __init__(self, x, y, image_path, text):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (300, 150))  # Adjust size as needed
        self.rect = self.image.get_rect(topleft=(x, y))
        self.text = text
        self.font = pygame.font.SysFont("cambria", 40)  # Font and size
        self.text_surf = self.font.render(self.text, True, (255, 255, 255))  # White text
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        surface.blit(self.text_surf, self.text_rect.topleft)

    def check_for_input(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# Initialize the button
button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 250, "button.png", "START")

# Game loop
game_active = False  # Start with the game not active
space_pressed = False  # Initialize space_pressed

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not game_active and button.check_for_input(event.pos):
                game_active = True
                platform_timer = pygame.time.get_ticks()  # Reset the platform timer when game starts
                spawn_initial_platforms()
                platform_start_time = None

    if game_active:
        screen.blit(background_image, (0, 0))
        
        keys = pygame.key.get_pressed()
        key = keys

        if key[pygame.K_d] or key[pygame.K_a]:
            player_movement_start_time = pygame.time.get_ticks()

        if key[pygame.K_d]:
            player.x += player_speed
            player_direction = 1
            is_moving_forward = True
            is_moving_backward = False
        elif key[pygame.K_a]:
            player.x -= player_speed
            player_direction = -1
            is_moving_forward = False
            is_moving_backward = True
        else:
            is_moving_forward = False
            is_moving_backward = False

        if key[pygame.K_w] and (can_jump or (can_double_jump and current_jumps < max_jumps)):
            player_y_velocity = jump
            can_jump = False
            can_double_jump = False
            current_jumps += 1

        player_y_velocity += gravity
        player.y += player_y_velocity

        on_ground = False
        for platform in platforms:
            if player.colliderect(platform):
                if player_y_velocity > 0:
                    player.bottom = platform.top
                    player_y_velocity = 0
                    can_jump = True
                    can_double_jump = True
                    current_jumps = 0
                    on_ground = True
                break

        if player.bottom > SCREEN_HEIGHT:
            player.bottom = SCREEN_HEIGHT
            player_y_velocity = 0
            can_jump = True
            can_double_jump = True
            current_jumps = 0

        if key[pygame.K_SPACE] and not space_pressed:
            projectile = Projectile(player.centerx + (player_size // 2 * player_direction), player.centery, projectile_speed, player_direction)
            player_projectiles.append(projectile)
            space_pressed = True
        elif not key[pygame.K_SPACE]:
            space_pressed = False

        for projectile in player_projectiles[:]:
            if not projectile.update():
                player_projectiles.remove(projectile)

        for enemy in enemies[:]:
            enemy.update(player.x)
            enemy_projectile = enemy.shoot(player.x, player.y)
            if enemy_projectile:
                enemy_projectiles.append(enemy_projectile)

        for projectile in enemy_projectiles[:]:
            if not projectile.update():
                enemy_projectiles.remove(projectile)
            elif player.colliderect(projectile.rect):
                player_health -= 1
                enemy_projectiles.remove(projectile)
                if player_health <= 0:
                    game_active = False

        for projectile in player_projectiles[:]:
            for enemy in enemies[:]:
                if projectile.rect.colliderect(enemy.rect):
                    enemy.hit_count += 1
                    player_projectiles.remove(projectile)
                    if enemy.hit_count >= 3:
                        enemies.remove(enemy)
                    break

        screen.blit(background_image_2, (background_scroll, 0))
        screen.blit(background_image_2, (background_scroll + background_image_2_width, 0))

        if background_scroll <= -background_image_2_width:
            background_scroll = 0

        spawn_new_platforms()
        update_coin_spawn()

        for platform in platforms:
            screen.blit(platform_image, platform)

        for coin in coins[:]:
            screen.blit(Fire_coin, coin)
            if player.colliderect(coin):
                pygame.mixer.Sound.play(coin_sound)
                coins.remove(coin)
                score += 1  # Increment score when coin is collected

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

        for projectile in player_projectiles:
            projectile.draw(screen)
        for projectile in enemy_projectiles:
            projectile.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        health_bar(screen, 10, 10, player_health, max_health)
        update_score_surface(screen, 10, 60, score)

    else:
        # Draw the start button
        screen.blit(background_image, (0, 0))  # Optionally redraw the background
        button.draw(screen)

    pygame.display.update()
    pygame.time.Clock().tick(60)
