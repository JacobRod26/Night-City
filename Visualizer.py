import pygame
import math
import random
import json

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI-Driven Audio Visualizer")
clock = pygame.time.Clock()

# Example: pretend this comes from your AI
ai_instructions = json.loads("""
{
  "dominant_band": "bass",
  "intensity": "high",
  "shapes": "radial_lines",
  "color_map": ["#FF0000", "#00FF00", "#0000FF"]
}
""")

# Example fake band data (replace with Demucs stream)
def get_fake_bands():
    return [random.random() for _ in range(32)]

def draw_visual(bands, instructions):
    screen.fill((0, 0, 0))  # background black

    cx, cy = WIDTH // 2, HEIGHT // 2
    num_bands = len(bands)
    angle_step = (2 * math.pi) / num_bands

    colors = [pygame.Color(c) for c in instructions["color_map"]]

    # Choose style from AI
    shape = instructions["shapes"]

    for i, value in enumerate(bands):
        angle = i * angle_step
        radius = 200 * value + 50  # scale band magnitude
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)

        color = colors[i % len(colors)]

        if shape == "radial_lines":
            pygame.draw.line(screen, color, (cx, cy), (x, y), 3)
        elif shape == "circles":
            pygame.draw.circle(screen, color, (int(x), int(y)), int(10 + 30 * value), 2)
        elif shape == "bars":
            pygame.draw.rect(screen, color, (i * 20, HEIGHT - (value * 300), 15, value * 300))

    pygame.display.flip()

# -----------------------------
# Main Loop
# -----------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    bands = get_fake_bands()  # Replace with Demucs data
    draw_visual(bands, ai_instructions)

    clock.tick(30)  # 30 FPS

pygame.quit()
