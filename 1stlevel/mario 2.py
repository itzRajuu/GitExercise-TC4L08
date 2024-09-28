import pygame
import sys
import time

pygame.init()

window_width = 1280
window_height = 720
window_size = (window_width, window_height)

screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Slugterra")

player_size = 50
player_x = (window_width - player_size) // 2
player_y = window_height - 2 * player_size
player_speed_y = 0  
player_speed = 3  

gravity = 0.5
jump = -10  
ground_level = window_height - player_size  

font = pygame.font.Font(None, 36)

projectile_speed = 5
enemy_projectile_speed = 2
player_projectiles = []
enemy_projectiles = []

enemy_size = 50
enemies = []
enemy_shoot_interval = 200  
enemy_speed = 0.5  

player_health = 3
max_health = 3

max_jumps = 2
current_jumps = 0

inventory = []  

player_image = pygame.image.load("Character/character_standing1.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (player_size, player_size))

slug1_frames = [
    pygame.image.load("fire_bullet3.png").convert_alpha(),
    pygame.image.load("fire_bullet1.png").convert_alpha(),
    pygame.image.load("fire_bullet2.png").convert_alpha(),
]

slug2_frames = [
    pygame.image.load("Frost.png").convert_alpha(),
    pygame.image.load("Frost1.png").convert_alpha(),
    pygame.image.load("Frost2.png").convert_alpha(),
]

enemy_image = pygame.image.load("enemy_slug.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (enemy_size, enemy_size))

ghoul_slug_frames = [
    pygame.image.load("ghoul_slug.png").convert_alpha(),
    pygame.image.load("ghoul_slug1.png").convert_alpha(),
    pygame.image.load("ghoul_slug2.png").convert_alpha(),
]

current_slug = 1
slug_frames = slug1_frames

class Projectile:
    def __init__(self, x, y, speed, direction):
        self.rect = pygame.Rect(x, y, 15, 5)  
        self.speed = speed
        self.direction = direction  

    def update(self):
        self.rect.x += self.speed * self.direction

    def draw(self, screen):
        pygame.draw.rect(screen, 'red', self.rect)

class SlugProjectile(Projectile):
    def __init__(self, x, y, speed, direction, frames, animation_speed):
        super().__init__(x, y, speed, direction)
        self.frames = frames
        self.num_frames = len(frames)
        self.current_frame = 0
        self.animation_speed = animation_speed
        self.animation_counter = 0
        self.image = self.frames[self.current_frame]

    def update(self):
        super().update()
        
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.image = self.frames[self.current_frame]

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, enemy_size, enemy_size)
        self.speed = enemy_speed  
        self.shoot_timer = 0  
        self.image = enemy_image  

    def update(self, player_x):
        if self.rect.x < player_x:
            self.rect.x += self.speed
        elif self.rect.x > player_x:
            self.rect.x -= self.speed

        self.shoot_timer += 1

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def shoot(self, player_x, player_y):
        if self.shoot_timer >= enemy_shoot_interval:
            self.shoot_timer = 0  
            direction = 1 if player_x >= self.rect.x else -1
            y_position = self.rect.y + self.rect.height // 2
            projectile_y = y_position - ghoul_slug_frames[0].get_height() // 2
            return SlugProjectile(self.rect.x, projectile_y, enemy_projectile_speed, direction, ghoul_slug_frames, animation_speed=10)
        return None

class Item:
    def __init__(self, x, y, width, height, item_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.item_type = item_type

    def draw(self, screen):
        pygame.draw.rect(screen, 'yellow', self.rect)

items = []
items.append(Item(500, ground_level - 20, 20, 20, "Slug 1"))
items.append(Item(700, ground_level - 20, 20, 20, "Slug 2"))

def draw_inventory(screen, font):
    inventory_surface = font.render(f"Inventory: {', '.join(inventory)}", True, 'black')
    screen.blit(inventory_surface, (10, 50))

def cutscene(dialogue, screen, top_bar_height=150, delay=0.05):
    running = True
    text_displayed = ""
    clock = pygame.time.Clock()

    for char in dialogue:
        text_displayed += char
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  
                    return

        pygame.draw.rect(screen, 'black', (0, 0, window_width, top_bar_height))

        text_surface = font.render(text_displayed, True, 'white')
        text_rect = text_surface.get_rect(center=(window_width // 2, top_bar_height // 2))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()

        time.sleep(delay)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  
                    running = False

        pygame.draw.rect(screen, 'black', (0, 0, window_width, top_bar_height))
        text_surface = font.render(text_displayed, True, 'white')
        text_rect = text_surface.get_rect(center=(window_width // 2, top_bar_height // 2))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()

def health_bar(screen, x, y, health, max_health):
    bar_width = 200
    bar_height = 12  
    pygame.draw.rect(screen, 'black', (x, y, bar_width, bar_height))
    fill_width = (health / max_health) * bar_width
    pygame.draw.rect(screen, 'red', (x, y, fill_width, bar_height))

def spawn_enemy():
    enemy_x = window_width - enemy_size
    enemies.append(Enemy(enemy_x, ground_level))

spawn_enemy()

cutscene("For centuries, the Darkbane, an ancient and evil race, were banished from Slugterra...", screen, top_bar_height=740, delay=0.01)
cutscene("Their dark ambitions, destroyed.", screen, top_bar_height=740, delay=0.01)
cutscene("But now, they have returned, more powerful and determined than ever.", screen, top_bar_height=740, delay=0.01)
cutscene("But in the face of darkness, there is hope.", screen, top_bar_height=740, delay=0.01)
cutscene("Eli Shane, a slugslinger, knows that the only way to stop the Darkbane is to save the Elemental Slugs.", screen, top_bar_height=740, delay=0.01)
cutscene("With his trusted companion, Burpy, by his side, Eli must embark on his most dangerous mission yet.", screen, top_bar_height=740, delay=0.01)

running = True
player_direction = 1
on_platform = False

while running:
    on_platform = False  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                projectile = SlugProjectile(
                    player_x + (player_size * player_direction),
                    player_y + player_size // 2,
                    projectile_speed,
                    player_direction,
                    slug_frames,
                    animation_speed=10  
                )
                player_projectiles.append(projectile)
            if event.key == pygame.K_UP:
                if player_y == ground_level or current_jumps < max_jumps:
                    player_speed_y = jump
                    current_jumps += 1  
            if event.key == pygame.K_1:
                current_slug = 1
                slug_frames = slug1_frames
                print("Switched to Slug 1")
            if event.key == pygame.K_2:
                current_slug = 2
                slug_frames = slug2_frames
                print("Switched to Slug 2")

    keys = pygame.key.get_pressed()

    player_speed_y += gravity
    player_y += player_speed_y

    if player_y > ground_level:
        player_y = ground_level
        player_speed_y = 0  
        current_jumps = 0  

    if keys[pygame.K_LEFT]:
        player_x -= player_speed
        player_direction = -1  
    elif keys[pygame.K_RIGHT]:
        player_x += player_speed
        player_direction = 1  

    for projectile in player_projectiles[:]:
        projectile.update()
        if projectile.rect.x > window_width or projectile.rect.x < 0:
            player_projectiles.remove(projectile)

    for projectile in enemy_projectiles[:]:
        projectile.update()
        if projectile.rect.x > window_width or projectile.rect.x < 0:
            enemy_projectiles.remove(projectile)

    for enemy in enemies:
        enemy.update(player_x)
        new_projectile = enemy.shoot(player_x, player_y)
        if new_projectile:
            enemy_projectiles.append(new_projectile)

    screen.fill('skyblue')

    screen.blit(player_image, (player_x, player_y))

    for projectile in player_projectiles:
        projectile.draw(screen)
    for projectile in enemy_projectiles:
        projectile.draw(screen)

    for enemy in enemies:
        enemy.draw(screen)

    health_bar(screen, 10, 10, player_health, max_health)

    for item in items:
        item.draw(screen)
        if item.rect.colliderect(pygame.Rect(player_x, player_y, player_size, player_size)):
            inventory.append(item.item_type)  
            items.remove(item)

    draw_inventory(screen, font)

    pygame.display.flip()

    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
