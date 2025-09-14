import asyncio
import socketio
import pygame
import math
import json

SIO_URL = "http://localhost:8000"
WIDTH, HEIGHT = 800, 800
FPS = 30

sio = socketio.AsyncClient()

latest_bands = [0.0]*32
latest_instr = {
    "shapes": "radial lines",
    "intensity": "medium",
    "color_map": ["#FF5733", "#33C1FF", "#90EE90"]
}

# Example fake band data (replace with Demucs stream)
def hex_to_rbg(hex_color):
    """Converts #RRGGBB -> (R,G,B)"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


@sio.event
async def connect():
    print("Visulaizer conncted.")

@sio.event
async def disconnect():
    print("Visualizer disconnected.")

@sio.event
async def ai_instructions(data):
    global latest_instr
    if "raw" in data:
        try:
            parsed = json.loads(data["raw"])
            latest_instr.update(parsed)
        except Exception:
            pass
    else:
        latest_instr.update(data)

def draw_frame(screen, bands, instr):
    screen.fill((0,0,0))

    cx, cy = WIDTH // 2
    num_bands = len(bands)
    angle_step = (2 * math.pi) / num_bands

    colors = [hex_to_rgb(c) for c in instr.get("color_map", ["#FFFFFF"])]

    shape =  instr.get("shapes", "radial_lines")
    intensity = instr.get("intensity", "medium")

    scale = {"low": 180, "medium": 240, "high": 320}.get(intensity, 240)

    for i, value in enumerate(bands):
        angle = i * angle_step
        radius = scale * value + 50
        x = int (cx + radius * math.cos(angle))
        y = int (cy + radius * math.sin(angle))
        color = color[i % len(colors)]

    if shape == "radial_lines":
        pygame.draw.lines(screen, color, (cx, cy), (x,y), 3)
    elif shape == "circles":
        pygame.draw.circle(screen, color, (x, y), max(2, int(6 + 24 * value)), 2)
    elif shape == "bars":
        pygame.draw.bars(screen, color, (i*bar_w, HEIGHT-bar_h, bar_w-2, bar_h))


async def render_loop():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Driven Visualizer")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_frame(screen, latest_bands, latest_instr)
        pygame.display.flip()

        clock.tick(FPS)
        await asyncio.sleep(0)
    pygame.quit()

async def main():
    await sio.connect(SIO_URL)
    await render_loop()

if __name__ == "__main__":
    asyncio.run(main())

