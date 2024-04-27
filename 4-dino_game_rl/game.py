import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Set up screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 200
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Game")

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)

# Set up player
player_width = 30
player_height = 30
player_rect = pygame.Rect(50, SCREEN_HEIGHT - player_height, player_width, player_height)
player_speed_y = 0
GRAVITY = 1

# Set up obstacles
obstacle_width = 20
obstacle_height = 50
obstacle_speed_x = -5
obstacle_list = []

# Set up game variables
score = 0
game_font = pygame.font.Font(None, 40)

# Functions
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)

def spawn_obstacle():
    if not obstacle_list or obstacle_list[-1].right < SCREEN_WIDTH - 200:
        obstacle_rect = pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT - obstacle_height, obstacle_width, obstacle_height)
        obstacle_list.append(obstacle_rect)

def move_obstacles():
    for obstacle in obstacle_list:
        obstacle.x += obstacle_speed_x

def draw_obstacles():
    for obstacle in obstacle_list:
        pygame.draw.rect(screen, BLACK, obstacle)

def check_collision():
    for obstacle in obstacle_list:
        if player_rect.colliderect(obstacle):
            return True
    return False

def closest_obstacle_distance():
    if obstacle_list:
        closest_dist = min([obstacle.left - player_rect.right for obstacle in obstacle_list if obstacle.left >= player_rect.right])
        return closest_dist if closest_dist > 0 else SCREEN_WIDTH
    else:
        return SCREEN_WIDTH

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if player_rect.bottom == SCREEN_HEIGHT:
                    player_speed_y = -15

    player_speed_y += GRAVITY
    player_rect.y += player_speed_y
    if player_rect.bottom > SCREEN_HEIGHT:
        player_rect.bottom = SCREEN_HEIGHT

    if random.randrange(0, 100) < 2:
        spawn_obstacle()

    move_obstacles()
    draw_obstacles()

    for obstacle in obstacle_list:
        if obstacle.right < 0:
            obstacle_list.remove(obstacle)
            score += 1

    if check_collision():
        running = False

    dist = closest_obstacle_distance()

    draw_text(f"Score: {score} ", game_font, BLACK, SCREEN_WIDTH // 2, 30)
    draw_text(f"Distance to closest obstacle: {dist}", game_font, BLACK, SCREEN_WIDTH // 2, 0)

    pygame.draw.rect(screen, PURPLE, player_rect)  # Draw the player as a purple rectangle
    pygame.display.update()
    clock.tick(30)
