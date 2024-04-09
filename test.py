import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Layering in Pygame")

# Create separate surfaces for different layers
background_surface = pygame.Surface((screen_width, screen_height))
foreground_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Draw function
def draw():
    # Clear the surfaces
    background_surface.fill(WHITE)
    foreground_surface.fill((0, 0, 0, 0))  # Clear with transparent color

    # Draw background elements (lower layer)
    pygame.draw.rect(background_surface, RED, (100, 100, 200, 200))
    pygame.draw.circle(background_surface, GREEN, (400, 300), 100)

    # Draw foreground elements (top layer)
    pygame.draw.line(foreground_surface, BLUE, (0, 0), (screen_width, screen_height), 5)
    pygame.draw.line(foreground_surface, BLUE, (0, screen_height), (screen_width, 0), 5)

    # Draw on top of everything
    pygame.draw.rect(foreground_surface, (255, 255, 0), (300, 200, 200, 100))  # Draw a yellow rectangle on top

    # Blit the surfaces onto the main display surface in the desired order
    screen.blit(background_surface, (0, 0))
    screen.blit(foreground_surface, (0, 0))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Draw everything
    draw()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
