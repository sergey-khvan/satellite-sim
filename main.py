import pygame
import sys

pygame.init()

# Set up your screen
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Circle and Line Collision Detection")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Circle properties
circle_radius = 30
circle_x, circle_y = 100, 300
circle_speed = 2

# Line properties
line_x1, line_y1 = 400, 100
line_x2, line_y2 = 400, 500
line_width = 5
line_speed = 1

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update circle position
    circle_x += circle_speed

    # Update line position
    line_y1 += line_speed
    line_y2 += line_speed

    # Clear the screen
    screen.fill(WHITE)

    # Draw the circle and line
    pygame.draw.circle(screen, RED, (circle_x, circle_y), circle_radius)
    pygame.draw.line(screen, RED, (line_x1, line_y1), (line_x2, line_y2), line_width)

    # Check for collision
    if (
        circle_x + circle_radius >= line_x1
        and circle_x - circle_radius <= line_x2
        and circle_y >= min(line_y1, line_y2)
        and circle_y <= max(line_y1, line_y2)
    ):
        print("Touch!")

    pygame.display.flip()
    pygame.time.delay(10)

pygame.quit()
sys.exit()
