import pygame

# Initialize Pygame
pygame.init()

# Set up display
window_size = 500
screen = pygame.display.set_mode((window_size, window_size))
pygame.display.set_caption("Colored Squares")

# Define colors (Pygame uses RGB tuples)
color_map = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "purple": (128, 0, 128),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "brown": (139, 69, 19),
    "gray": (128, 128, 128),
    "cyan": (0, 255, 255)
}

# List of colors in order
colors = [
    "red", "green", "blue", "purple", "yellow",
    "orange", "pink", "brown", "gray", "cyan"
]

square_size = 80
margin = 20
cols = 5

# Main loop
running = True
while running:
    screen.fill((255, 255, 255))  # Fill background with white
    for idx, color in enumerate(colors):
        row = idx // cols
        col = idx % cols
        x = margin + col * (square_size + margin)
        y = margin + row * (square_size + margin)
        pygame.draw.rect(screen, color_map[color], (x, y, square_size, square_size))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, square_size, square_size), 2)  # Black border
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
