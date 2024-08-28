import pygame
import sys

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Slugterra Game")
main_font = pygame.font.SysFont("cambria", 50)

# Load the background image
background_image = pygame.image.load('Slug.Background.jpeg')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

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

# Load and scale the button image
button_surface = pygame.image.load("button.png")
button_surface = pygame.transform.scale(button_surface, (400, 150))
button = Button(button_surface, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 200, "Start")

player = pygame.Rect((300, 250, 50, 50))

# Display the background image for 2 seconds
screen.blit(background_image, (0, 0))
pygame.display.update()
pygame.time.wait(2000)

# Run the main game loop
run = True
game_active = False  # Variable to track whether the game has started
while run:
    screen.fill((0, 0, 0))  # Fill the screen with black to clear the previous frame

    if not game_active:
        # Display the background and start button
        screen.blit(background_image, (0, 0))
        button.changeColour(pygame.mouse.get_pos())
        button.update()
    else:
        # Game logic
        pygame.draw.rect(screen, (255, 0, 0), player)

        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            player.move_ip(-1, 0)
        elif key[pygame.K_d]:
            player.move_ip(1, 0)
        elif key[pygame.K_w]:
            player.move_ip(0, -1)
        elif key[pygame.K_s]:
            player.move_ip(0, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button.checkForInput(pygame.mouse.get_pos()) and not game_active:
                game_active = True  # Start the game when the button is clicked

    pygame.display.update()

pygame.quit()
