import pygame
import sys
import time
import random

pygame.init()
info = pygame.display.Info()
window_width = info.current_w
window_height = info.current_h
window_size = (window_width, window_height)


screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Slugterra")

background = pygame.image.load('firebg.jpg')
background = pygame.transform.scale(background, (window_width, window_height))


player_w = 52
player_h = 69
player_x = window_width//2 
player_y = window_height - 2 * player_h
player_speed_y = 0  
player_speed = 5

gravity = 0.5
jump = -10  
ground_level = window_height - player_h  

font = pygame.font.Font(None, 36)

projectile_speed = 10
player_projectiles = []
enemy_projectiles = []
last_shot_time = pygame.time.get_ticks()

# Platforms
platforms = []        

# Enemy 
enemy_w = 55 
enemy_h = 69
enemies = []
enemy_projectile_speed = 10  
enemy_shoot_interval = 100
enemy_speed = 2
enemy_image = pygame.image.load('enemi.png')
boss_img = pygame.image.load('boss.png')

joules_img = pygame.image.load('joules.png')
banger_img = pygame.image.load('banger.png')

# Player 
player_health = 5
max_health = 5

# Double jump 
max_jumps = 2
current_jumps = 0

enemies_killed = 0

inventory = []  # Player inventory

available_projectiles = ["normal"]  # Start with "normal" projectile type
current_projectile_index = 0  # Index to track current selected projectile type

bullet_image = pygame.image.load('fire_bullet1.png')
bullet_image = pygame.transform.scale(bullet_image, (40, 25))
banger_image = pygame.image.load('banger2.png')
banger_image = pygame.transform.scale(banger_image,(40,25))
joules_image = pygame.image.load('joules2.png')
joules_image = pygame.transform.scale(joules_image,(40,25))
enemy_bullet_image = pygame.image.load('enemy_bullet.png').convert_alpha()
enemy_bullet_image = pygame.transform.scale(enemy_bullet_image, (40, 25))
flipped_bullet = pygame.transform.flip(bullet_image, True, False)

# Projectile properties dictionary
projectile_properties = {
    "normal": {"speed": 12, "damage": 7, "image": bullet_image, "shot_interval": 300},
    "Banger": {"speed": 15, "damage": 100, "image": banger_image, "shot_interval": 1000},
    "Joules": {"speed": 12, "damage": 10, "image": joules_image, "shot_interval": 100},
    "enemy": {"speed": 12, "damage": 10, "image": enemy_bullet_image, "shot_interval": 100}
}
 


class Projectile:
    def __init__(self, x, y, direction, projectile_type="normal" ):
        self.rect = pygame.Rect(x, y, 40, 20)  
        #self.speed = speed
        self.direction = direction
        self.type = projectile_type
        self.speed = projectile_properties[projectile_type]["speed"]
        self.damage = projectile_properties[projectile_type]["damage"]
        self.image = projectile_properties[projectile_type]["image"]
        
  

    def update(self):
        self.rect.x += self.speed * self.direction

    def draw(self, screen):
        if self.direction == 1:
          screen.blit(self.image, self.rect.topleft)
        else:
          # Assuming `self.image` is the projectile image, and `self.rect` holds its position
          screen.blit(pygame.transform.flip(self.image, True, False), self.rect)


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, enemy_w, enemy_h)
        self.speed = enemy_speed  
        self.shoot_timer = 0  
        self.health = 30
        self.speed_y = 0  # Vertical speed for gravity

    def apply_gravity(self):
        self.speed_y += gravity
        self.rect.y += self.speed_y

    def update(self, player_x):
        self.apply_gravity()  # Apply gravity in each update call
        
        # Check if the enemy is on a platform or the ground
        on_platform = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.speed_y > 0:
                self.rect.y = platform.rect.top - enemy_h
                self.speed_y = 0
                on_platform = True
        
        # Check ground collision
        if self.rect.bottom >= window_height:
            self.rect.bottom = window_height
            self.speed_y = 0
            on_platform = True
        
        if not on_platform:
            self.apply_gravity()

        # Horizontal movement
        if self.rect.x < player_x:
            self.rect.x += self.speed
        elif self.rect.x > player_x:
            self.rect.x -= self.speed

        self.shoot_timer += 1

    def draw(self, screen):
        direction = 1 if player_x >= self.rect.x else -1        
        if direction == 1:
            screen.blit(enemy_image,self.rect)
        else:
            screen.blit(pygame.transform.flip(enemy_image, True, False),self.rect)

    def shoot(self, player_x, player_y):
        if self.shoot_timer >= enemy_shoot_interval:
            self.shoot_timer = 0  
            direction = 1 if player_x >= self.rect.x else -1
            return Projectile(self.rect.x , self.rect.y + self.rect.height / 2, direction, projectile_type="enemy")
        return None

class Platform:
    def __init__(self, x, y, width, height, image_path):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path)  # Load the image
        self.image = pygame.transform.scale(self.image, (width, height))  # Resize the image to fit platform size

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def spawn_enemy():
    global enemies_killed
    if enemies_killed < 10:
        # Randomly choose one of the 4 corners (0: top-left, 1: top-right, 2: bottom-left, 3: bottom-right)
        corner = random.choice([0, 1, 2, 3])
        
        if corner == 0:  # Top-left corner
            enemy_x = 0
            enemy_y = 0
        elif corner == 1:  # Top-right corner
            enemy_x = window_width - enemy_w
            enemy_y = 0
        elif corner == 2:  # Bottom-left corner
            enemy_x = 0
            enemy_y = window_height//2 
        elif corner == 3:  # Bottom-right corner
            enemy_x = window_width - enemy_w
            enemy_y = window_height//2 

        enemies.append(Enemy(enemy_x, enemy_y))

        
 
class Item:
    def __init__(self, x, y, width, height, item_type,image, projectile_type=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.item_type = item_type
        self.image = image
        self.projectile_type = projectile_type

    def draw(self, screen):
        screen.blit(self.image,self.rect)

#class Obstacle:
 #   def __init__(self, x, y, width, height, color='gray'):
  #      self.rect = pygame.Rect(x, y, width, height)
   #     self.color = color
#
 #   def draw(self, screen):
  #      pygame.draw.rect(screen, self.color, self.rect)

class Trap:
    def __init__(self, x, y, width, height,  color='red'):
        self.rect = pygame.Rect(x, y, width, height)
        self.damage = 1
        self.color = color
        self.has_collided = False  # Track collision state

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def check_collision(self, player_rect, player_health):
        # Check if the player is colliding with the trap
        if player_rect.colliderect(self.rect):
            if not self.has_collided:  # Only apply damage if not already colliding
                player_health -= self.damage
                self.has_collided = True  # Set collision flag to avoid multiple damage applications
        else:
            # Reset the flag if the player is no longer in contact with the trap
            self.has_collided = False
        return player_health

class Boss:
    def __init__(self, x, y):
        # Initialize the boss at the given (x, y) position
        self.rect = pygame.Rect(x, y, enemy_w * 2, enemy_h * 2)  # Boss is larger
        self.speed = enemy_speed * 2  # Boss is faster
        self.health = 100   # Boss has more health
        self.shoot_timer = 0
        self.jump_force = -12  # Jump force for the boss
        self.speed_y = 0  # Vertical speed for jumping and falling
        self.gravity = 0.5  # Gravity value for the boss
        self.on_ground = False  # Check if the boss is on the ground

    def apply_gravity(self):
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        # Ensure the boss doesn't fall through the ground
        if self.rect.bottom >= window_height:
            self.rect.bottom = window_height
            self.speed_y = 0
            self.on_ground = True

    def move_towards_player(self, player_x):
        # Move horizontally towards the player
        if self.rect.x < player_x:
            self.rect.x += self.speed
        elif self.rect.x > player_x:
            self.rect.x -= self.speed

    def jump_towards_player(self, player_y):
        # If the player is higher than the boss and the boss is on the ground, jump
        if self.on_ground and self.rect.y > player_y:
            self.speed_y = self.jump_force
            self.on_ground = False  # Boss is not on the ground after jumping

    def update(self, player_x, player_y):
        # Apply gravity to the boss
        self.apply_gravity()

        # Check if the boss is on the ground (also considering platforms if you have them)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.speed_y > 0:
                self.rect.bottom = platform.rect.top  # Align the bottom of the boss with the top of the platform
                self.speed_y = 0  # Stop vertical movement
                self.on_ground = True

        # If the boss hits the ground, reset vertical speed and mark it as on the ground
        if self.rect.bottom >= window_height:
            self.rect.bottom = window_height
            self.speed_y = 0
            self.on_ground = True

        # Move towards the player's position horizontally
        self.move_towards_player(player_x)

        # Jump if the player is higher than the boss
        self.jump_towards_player(player_y)

        # Update shooting timer
        self.shoot_timer += 1

    def draw(self, screen, player_x):
        # Determine if the boss should face the player
        direction = 1 if player_x >= self.rect.x else -1
        if direction == 1:
            screen.blit(boss_img, self.rect)
        else:
            screen.blit(pygame.transform.flip(boss_img, True, False), self.rect)

    def shoot(self, player_x, player_y):
        # Boss shoots more frequently than regular enemies
        if self.shoot_timer >= enemy_shoot_interval / 2:
            self.shoot_timer = 0
            direction = 1 if player_x >= self.rect.x else -1
            # Create a projectile that moves towards the player
            return Projectile(self.rect.x, self.rect.y + self.rect.height / 2, direction, projectile_type="enemy")
        return None

    
  

#obstacles = [Obstacle(400, window_height - 50, 100, 50), Obstacle(800, window_height - 50, 200, 50)]
traps = [ Trap(1120, window_height - 10, 150, 10)]

# Add items to the game
items = []
items.append(Item(500, 400 - 30, 20, 30, "Banger ",banger_img, projectile_type="Banger"))
items.append(Item(700, window_height - 30, 20, 20, "Joules ",joules_img, projectile_type="Joules"))

# Inventory display
def draw_inventory(screen, font):
    inventory_surface = font.render(f"Inventory: {', '.join(inventory)}", True, 'grey')
    screen.blit(inventory_surface, (10, 40))  # Display the inventory on the screen

# Display the current projectile type
def draw_current_projectile_type(screen, font, current_type):
    projectile_type_surface = font.render(f"Slug: {current_type}", True, 'white')
    screen.blit(projectile_type_surface, (10, 70))

def load_sprite_sheet(filename, frame_width, frame_height):
    sprite_sheet = pygame.image.load(filename).convert_alpha()
    frames = []
    for i in range(sprite_sheet.get_width() // frame_width):
        frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames

run_sprites = load_sprite_sheet('plyridle.png',48 , 69)  
jump_sprites = load_sprite_sheet('plyridle.png', 48, 69)  
run_back_sprites = load_sprite_sheet('plyrback.png', 48, 69)  
idle_sprites = load_sprite_sheet('plyridle.png', 48, 69)  


def cutscene(dialogue, screen, top_bar_height=150, delay=0.05):
    running = True
    text_displayed = ""
    clock = pygame.time.Clock()

    for char in dialogue:
        text_displayed += char
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
              running = False
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

# Add initial platforms
#platforms.append(Platform(300, 100, 1000, 20, "platform1.png"))
#platforms.append(Platform(0, 200, 800, 20, "platform1.png"))
platforms.append(Platform(400, 300, 500, 40, "iceplatform1.png"))
platforms.append(Platform(200, 400, 300, 40, "iceplatform1.png"))
platforms.append(Platform(0, 400, 300, 40, "iceplatform1.png"))
platforms.append(Platform(400, 500, 800, 20, "iceplatform1.png"))
platforms.append(Platform(900, 500, 800, 20, "iceplatform1.png"))
platforms.append(Platform(0, 600, 500, 20, "iceplatform1.png"))
platforms.append(Platform(600, 600, 500, 40, "iceplatform1.png"))
platforms.append(Platform(900, 600, 200, 40, "iceplatform1.png"))



#cutscene("For centuries, the Darkbane, an ancient and evil race, were banished from Slugterra...", screen, top_bar_height=740, delay=0.01)
#cutscene("Their dark ambitions, destroyed.", screen, top_bar_height=740, delay=0.01)
#cutscene("But now, they have returned, more powerful and determined than ever.", screen, top_bar_height=740, delay=0.01)
#cutscene("But in the face of darkness, there is hope.", screen, top_bar_height=740, delay=0.01)
#cutscene("Eli Shane, a slugslinger, knows that the only way to stop the Darkbane is to save the Elemental Slugs.", screen, top_bar_height=740, delay=0.01)
#cutscene("With his trusted companion, Burpy, by his side, Eli must embark on his most dangerous mission yet.", screen, top_bar_height=740, delay=0.01)
spawn_enemy()

running = True
player_direction = 1
on_platform = False
normal_enemies_killed = 0  # Track how many normal enemies have been killed
boss_spawned = False  # Track if the boss has been spawned
boss = None
enemy_spawned = 1 
enemy_spawn_interval = 1000  # 5000 milliseconds = 5 seconds
last_enemy_spawn_time = pygame.time.get_ticks()

current_frame = 0
frame_counts = {
    'run': len(run_sprites),
    'jump': len(jump_sprites),
    'run_back': len(run_back_sprites),
    'idle': len(idle_sprites)
}

action = 'idle' 

while running:
    on_platform = False
    current_time = pygame.time.get_ticks()  
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if player_y == ground_level or current_jumps < max_jumps:
                    player_speed_y = jump
                    current_jumps += 1
                    action = 'jump'  # Handle double jumps
            if event.key == pygame.K_SPACE:
                # Shoot a projectile based on current ammo type
                shot_interval = projectile_properties[available_projectiles[current_projectile_index]]["shot_interval"]
                
                if current_time - last_shot_time >= shot_interval:
                    # Shoot a projectile based on current ammo type
                    projectile = Projectile(player_x + (player_w // 2)-20 , player_y + (player_h // 2) , player_direction, available_projectiles[current_projectile_index])
                    player_projectiles.append(projectile)
                    last_shot_time = current_time  # Update last shot time after firing
            if event.key == pygame.K_e:  # Press 'E' to switch to the next projectile type
                current_projectile_index = (current_projectile_index + 1) % len(available_projectiles)
            if event.key == pygame.K_q:  # Press 'Q' to switch to the previous projectile type
                current_projectile_index = (current_projectile_index - 1) % len(available_projectiles)

    
    keys = pygame.key.get_pressed()

    player_speed_y += gravity
    player_y += player_speed_y

    if player_y > ground_level:
        player_y = ground_level
        player_speed_y = 0  
        current_jumps = 0  

    if keys[pygame.K_a]:
        player_x -= player_speed
        player_direction = -1 
        action = 'run_back' 
    elif keys[pygame.K_d]:
        player_x += player_speed
        player_direction = 1 
        action = 'run' 
    else:
        action = 'idle'
    

    player_x = max(0, min(player_x, window_width - player_w))

    player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
    pygame.draw.rect(screen, 'white', player_rect)
    screen.blit(background, (0, 0))
    

    

    # Update player collision with platforms
    for platform in platforms:
        if player_rect.colliderect(platform.rect) and player_speed_y > 0:
            player_y = platform.rect.top - player_h
            player_speed_y = 0
            current_jumps = 0  # Reset jump count when on a platform
            on_platform = True

        platform.draw(screen)

    # Draw items and check for collisions
    for item in items[:]:
        item.draw(screen)
        if player_rect.colliderect(item.rect):
            if item.item_type not in inventory:
                inventory.append(item.item_type)  # Add item to inventory
            if item.projectile_type and item.projectile_type not in available_projectiles:
                available_projectiles.append(item.projectile_type)  # Add projectile type to available types
            items.remove(item)  # Remove the item from the world


    for projectile in player_projectiles[:]:
        projectile.update()
        if projectile.rect.x < 0 or projectile.rect.x > window_width:
            player_projectiles.remove(projectile)
        projectile.draw(screen)

    for enemy in enemies[:]:
        enemy.update(player_x)
        enemy.draw(screen)

        enemy_projectile = enemy.shoot(player_x, player_y)
        if enemy_projectile:
            enemy_projectiles.append(enemy_projectile)

        #if player_rect.colliderect(enemy.rect):
        #    cutscene("You got touched!", screen)
         #   running = False
        
        if enemy_spawned < 10:
           if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
              spawn_enemy()  # Call the function to spawn an enemy
              enemy_spawned += 1
              last_enemy_spawn_time = current_time  # Update the last spawn time

        for projectile in player_projectiles[:]:
         if projectile.rect.colliderect(enemy.rect):
            enemy.health -= projectile.damage  # Reduce enemy health by projectile damage
            player_projectiles.remove(projectile)  # Remove the projectile after hit

            if enemy.health <= 0:
                    enemies.remove(enemy)
                    #normal_enemies_killed += 1    
                    enemies_killed += 1
                    if enemies_killed == 10:                    
                        if not boss_spawned:
                            boss = Boss(0, window_height)  # Spawn boss
                            boss_spawned = True
                    break
               
                
        for projectile in player_projectiles[:]:
            if projectile.rect.colliderect(enemy.rect):
                enemies.remove(enemy)
                player_projectiles.remove(projectile)
                #cutscene("Enemy killed!", screen)
                spawn_enemy()  
                break
    
    if boss:
        boss.update(player_x,player_y)
        boss.draw(screen,player_x)

        boss_projectile = boss.shoot(player_x, player_y)
        if boss_projectile:
            enemy_projectiles.append(boss_projectile)

        if player_rect.colliderect(boss.rect):
            cutscene("You got touched by the boss!", screen)
            running = False

        for projectile in player_projectiles[:]:
            if projectile.rect.colliderect(boss.rect):
                boss.health -= projectile.damage
                player_projectiles.remove(projectile)

                if boss.health <= 0:
                    cutscene("You defeated the boss!", screen)
                    running = False  
                    break

    for enemy_projectile in enemy_projectiles[:]:
        enemy_projectile.update()
        if enemy_projectile.rect.x < 0:
            enemy_projectiles.remove(enemy_projectile)
        enemy_projectile.draw(screen)

        if enemy_projectile.rect.colliderect(player_rect):
            player_health -= 1
            enemy_projectiles.remove(enemy_projectile)
            if player_health <= 0:
                cutscene("You died!!", screen)
                running = False  

    for player_projectile in player_projectiles[:]:
        for enemy_projectile in enemy_projectiles[:]:
            if player_projectile.rect.colliderect(enemy_projectile.rect):
                player_projectiles.remove(player_projectile)
                enemy_projectiles.remove(enemy_projectile)
                break
        
    
    
    if  action == 'run':
        screen.blit(run_sprites[current_frame], (player_x, player_y))
    elif action == 'run_back':
        screen.blit(run_back_sprites[current_frame], (player_x, player_y))
    elif action == 'jump':
        # Display jump animation in the correct direction
        if player_direction == 1:
            screen.blit(jump_sprites[current_frame], (player_x, player_y))
        else:
            flipped_jump = pygame.transform.flip(jump_sprites[current_frame], True, False)
            screen.blit(flipped_jump, (player_x, player_y))
    else:  # Idle state
        if player_direction == 1:
            screen.blit(idle_sprites[current_frame], (player_x, player_y))
        else:
            flipped_idle = pygame.transform.flip(idle_sprites[current_frame], True, False)
            screen.blit(flipped_idle, (player_x, player_y))


 #   for obstacle in obstacles:
  #   obstacle.draw(screen)

    #  Check if the player is colliding with the obstacle
   #  if player_rect.colliderect(obstacle.rect):
    #    if player_speed_y > 0:  # If falling down
     #       player_y = obstacle.rect.top - player_size
      #      player_speed_y = 0  # Stop vertical movement after landing on the obstacle
      #      current_jumps = 0  # Reset jump count when landing on an obstacle
      #  elif keys[pygame.K_d] and player_rect.right > obstacle.rect.left:
      #      player_x = obstacle.rect.left - player_size
      #  elif keys[pygame.K_a] and player_rect.left < obstacle.rect.right:
      #      player_x = obstacle.rect.right

    for trap in traps:
       trap.draw(screen)
       player_health = trap.check_collision(player_rect, player_health)  # Check for trap collisions and reduce health
       if player_health <= 0:
        cutscene("You diedd!", screen)
        running = False

    
    draw_inventory(screen, font)
    draw_current_projectile_type(screen, font, available_projectiles[current_projectile_index])

    
    health_bar(screen, 10, 10, player_health, max_health)

    pygame.display.flip()

    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()      