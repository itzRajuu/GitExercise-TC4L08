import turtle
import pygame
import sys
import time

# Initialize global variables
walls = []
door_position = None

def open_combat_window():
    pygame.init()
    combat_win = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Combat Game")

    bg_image = pygame.image.load("background.jpg")  

    player_rect = pygame.Rect(100, 500, 60, 80)      
    enemy_rect = pygame.Rect(600, 500, 60, 80) 
    bullets = []  # List to hold player bullets
    enemy_bullets = []  # List to hold enemy bullets

    # Load animation frames for the enemy
    animation_frames = [pygame.image.load(f"frame_{i}.png") for i in range(1, 13)]  # Ensure these files exist
    current_frame = 0
    
    clock = pygame.time.Clock()

    player_health = 100
    enemy_health = 100

    player_speed = 10
    gravity = 2
    jump_power = -20
    player_velocity_y = 0
    is_jumping = False

    last_enemy_shot = time.time()
    enemy_shoot_interval = 3 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet_rect = pygame.Rect(player_rect.right, player_rect.top + player_rect.height // 2 - 5, 15, 10)
                    bullets.append(bullet_rect)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_rect.x += player_speed
        if keys[pygame.K_UP] and not is_jumping:  
            is_jumping = True
            player_velocity_y = jump_power

        player_velocity_y += gravity
        player_rect.y += player_velocity_y

        if player_rect.y >= 500:
            player_rect.y = 500
            is_jumping = False

        if player_rect.x < 0:
            player_rect.x = 0
        if player_rect.x > 800 - player_rect.width:
            player_rect.x = 800 - player_rect.width

        for bullet in bullets[:]:
            bullet.x += 15  
            if bullet.x > 800:  
                bullets.remove(bullet)
            if bullet.colliderect(enemy_rect):
                enemy_health -= 10  
                bullets.remove(bullet)  
                if enemy_health <= 0:
                    print("Enemy defeated!")
                    pygame.quit()
                    sys.exit()

        current_time = time.time()
        if current_time - last_enemy_shot >= enemy_shoot_interval:
            enemy_bullet = pygame.Rect(enemy_rect.left - 25, enemy_rect.top + enemy_rect.height // 2 - 5, 20, 10)
            enemy_bullets.append(enemy_bullet)
            last_enemy_shot = current_time

        for bullet in enemy_bullets[:]:
            bullet.x -= 10  
            if bullet.x < 0:  
                enemy_bullets.remove(bullet)
            if bullet.colliderect(player_rect):
                player_health -= 10  
                enemy_bullets.remove(bullet)  
                if player_health <= 0:
                    print("Player defeated!")
                    pygame.quit()
                    sys.exit()

        # Drawing
        combat_win.blit(pygame.transform.scale(bg_image, (800, 600)), (0, 0))
        pygame.draw.rect(combat_win, (0, 255, 0), player_rect)  

        # Draw enemy with animation
        combat_win.blit(animation_frames[current_frame], (enemy_rect.x, enemy_rect.y))

        for bullet in bullets:
            pygame.draw.rect(combat_win, (255, 255, 0), bullet) 
        for bullet in enemy_bullets:
            pygame.draw.rect(combat_win, (0, 0, 255), bullet)  

        player_health_bar_width = 200 * (player_health / 100)
        pygame.draw.rect(combat_win, (255, 0, 0), (50, 20, 200, 20))  
        pygame.draw.rect(combat_win, (0, 255, 0), (50, 20, player_health_bar_width, 20))  
        
        enemy_health_bar_width = 200 * (enemy_health / 100)
        pygame.draw.rect(combat_win, (255, 0, 0), (combat_win.get_width() - 250, 20, 200, 20))  
        pygame.draw.rect(combat_win, (0, 255, 0), (combat_win.get_width() - 250, 20, enemy_health_bar_width, 20))  

        # Update the frame for animation
        current_frame = (current_frame + 1) % len(animation_frames)

        pygame.display.update()
        clock.tick(30)

def setup_maze(level):
    global door_position, walls

    pen.clearstamps() 
    walls.clear()  

    # Collect wall and door positions without drawing
    for y in range(len(level)):
        for x in range(len(level[y])):
            character = level[y][x]
            screen_x = -288 + (x * 24)
            screen_y = 288 - (y * 24)

            if character == "X":
                walls.append((screen_x, screen_y))
            elif character == "P":
                player.goto(screen_x, screen_y)
            elif character == "D":
                door_position = (screen_x, screen_y)

    # Draw walls and door after processing the whole level
    for wall_pos in walls:
        pen.goto(wall_pos)
        pen.shape("wall.img.gif")
        pen.stamp()

    if door_position is not None:
        pen.goto(door_position)
        pen.shape("door.maze.gif")  
        pen.stamp()
    else:
        print("Door position not set.")

win = turtle.Screen()
win.bgpic("sword_bg.gif")
win.title("Infinite Maze")
win.setup(700, 700)
win.register_shape("wall.img.gif")
win.register_shape("door.maze.gif")
win.register_shape("Standing.gif") 
win.register_shape("Left.gif")  
win.register_shape("Right.gif") 
win.register_shape("Monster1.5.gif")
win.register_shape("Monster2.5.gif")
win.register_shape("Monster3.5.gif")
win.register_shape("Monster4.5.gif")
win.register_shape("Monster5.5.gif")

class Pen(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("wall.img.gif")
        self.color("white")
        self.penup()
        self.speed(0)

class Player(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("Standing.gif")  
        self.color("green")
        self.penup()
        self.speed(0)
        self.goto(-264, 264)  

    def move_up(self):
        self.shape("Standing.gif")  
        new_x = self.xcor()
        new_y = self.ycor() + 24
        if (new_x, new_y) not in walls: 
            self.goto(new_x, new_y)
            check_for_collision()

    def move_down(self):
        self.shape("Standing.gif") 
        new_x = self.xcor()
        new_y = self.ycor() - 24
        if (new_x, new_y) not in walls:  
            self.goto(new_x, new_y)
            check_for_collision()

    def move_left(self):
        self.shape("Left.gif")  
        new_x = self.xcor() - 24
        new_y = self.ycor()
        if (new_x, new_y) not in walls:  
            self.goto(new_x, new_y)
            check_for_collision()

    def move_right(self):
        self.shape("Right.gif")  
        new_x = self.xcor() + 24
        new_y = self.ycor()
        if (new_x, new_y) not in walls: 
            self.goto(new_x, new_y)
            check_for_collision()

    def check_if_at_door(self):
        if (self.xcor(), self.ycor()) == door_position:
            turtle.bye()

class Monster(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.frames = ["Monster1.5.gif", "Monster2.5.gif", "Monster3.5.gif", "Monster4.5.gif", "Monster5.5.gif"]
        self.frame_index = 0
        self.shape(self.frames[self.frame_index])
        self.penup()
        self.speed(0)
        self.goto(250, -310)

    def animate(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.shape(self.frames[self.frame_index])
        turtle.ontimer(self.animate, 200)  

level_1 = [
    "XXXXXXXXXXXXXXXXXXXXXXXXX",
    "XP  XXXXXXX          XXXXX",
    "X  XXXXXXX  XXXXXX  XXXXX",
    "X       XX  XXXXXX  XXXXX",
    "X       XX  XXX        XX",
    "XXXXXX  XX  XXX        XX",
    "XXXXXX  XX  XXXXXX  XXXXX",
    "XXXXXX  XX    XXXX  XXXXX",
    "X  XXX        XXXX  XXXXX",
    "X  XXX  XXXXXXXXXXXXXXXXX",
    "X         XXXXXXXXXXXXXXX",
    "X                XXXXXXXX",
    "XXXXXXXXXX       XXXXX  X",
    "XXXXXXXXXXXXX    XXXXX  X",
    "XXX  XXXXXXXX           X",
    "XXX                     X",
    "XXX          XXXXXXXXXXXX",
    "XXXXXXXXXX   XXXXXXXXXXXX",
    "XXXXXXXXXX              X",
    "XX    XXXX              X",
    "XX    XXXXXXXXXXXX   XXXX",
    "X             XXXX   XXXX",      
    "X                    XXXX",
    "XXXXXXXXXXXXXX  XX   XXXX",
    "XXXXXXXXXXXXXXXXXXXX   XX",
    "XXXXXXXXXXXXXXXXXXXXX   D"
]

pen = Pen()
player = Player()
monster = Monster()
walls = []
door_position = None

setup_maze(level_1)
monster.animate()

def check_for_collision():
    if player.distance(monster) < 24:
        turtle.bye()  
        open_combat_window()

win.listen()
win.onkey(player.move_up, "Up")
win.onkey(player.move_down, "Down")
win.onkey(player.move_left, "Left")
win.onkey(player.move_right, "Right")
win.onkey(open_combat_window, "space")  

turtle.ontimer(check_for_collision, 100)  # Check every 100ms

turtle.mainloop()