import socketio
import asyncio
import base64
import io
import json
import pygame
import math
from PIL import Image

# --- Setup ---
WIDTH, HEIGHT = 800, 600
pygame.display.init()
screen = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

sio = socketio.AsyncClient()

# Default visualization plan (until AI sends one)
current_instructions = {
    "dominant_band": "bass",
    "intensity": "low",
    "shapes": "circles",
    "color_map": ["#FFFFFF"]
}
eq_data = {}

# --- Helpers ---
def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def render_visuals(instructions, eq_data):
    screen.fill((0, 0, 0))

    dominant_band = instructions.get("dominant_band", "bass")
    intensity = instructions.get("intensity", "medium")
    shape = instructions.get("shapes", "circles")
    colors = [hex_to_rgb(c) for c in instructions.get("color_map", ["#FFFFFF"])]

    # Map intensity to scale
    intensity_map = {"low": 50, "medium": 120, "high": 250}
    scale = intensity_map.get(intensity, 100)

    cx, cy = WIDTH // 2, HEIGHT // 2
    level = eq_data.get(dominant_band, 0.5) * scale

    if shape == "radial_lines":
        for i, col in enumerate(colors):
            angle = (i / len(colors)) * 360
            rad = angle * 3.14 / 180
            x = int(cx + level * math.cos(rad))
            y = int(cy + level * math.sin(rad))
            pygame.draw.line(screen, col, (cx, cy), (x, y), 6)

    elif shape == "circles":
        for i, col in enumerate(colors):
            radius = int(level * (i + 1) / len(colors)) + 30
            pygame.draw.circle(screen, col, (cx, cy), radius, 0)

    elif shape == "bars":
        total_bars = len(colors)
        bar_spacing = 20  # space between bars

        # Calculate bar width based on available width minus spacing
        total_spacing = bar_spacing * (total_bars - 1)
        max_bar_width = 200  # or any max width you want per bar
        total_bars_width = total_bars * max_bar_width + total_spacing

        # Calculate starting X so bars are centered
        start_x = (WIDTH - total_bars_width) // 2

        for i, col in enumerate(colors):
            bar_height = 300 + int(level * (i + 1) / len(colors))
            x = start_x + i * (max_bar_width + bar_spacing)
            pygame.draw.rect(screen, col, (x, HEIGHT - bar_height, max_bar_width, bar_height))

def send_frame():
    raw_str = pygame.image.tostring(screen, "RGB")
    img = Image.frombytes("RGB", (WIDTH, HEIGHT), raw_str)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    frame_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    asyncio.create_task(sio.emit("frame", {"frame_b64": frame_b64}))

# --- Socket.IO Events ---
@sio.event
async def connect():
    print("Connected to server (Visualizer)")

@sio.event
async def disconnect():
    print("Disconnected from server (Visualizer)")

@sio.on("ai_instructions")
async def on_ai_instructions(data):
    global current_instructions
    try:
        current_instructions = json.loads(data) if isinstance(data, str) else data
        print("Updated AI instructions:", current_instructions)
    except Exception as e:
        print("Failed to parse ai_instructions:", e)

@sio.on("eq_data")
async def on_eq_data(data):
    global eq_data
    eq_data = data.get("bands", {})

# --- Render Loop ---
async def render_loop():
    while True:
        render_visuals(current_instructions, eq_data)
        send_frame()
        await asyncio.sleep(1 / 15)  # ~15 FPS

async def main():
    await sio.connect("http://localhost:8000")
    asyncio.create_task(render_loop())  # run visuals loop in background
    await sio.wait()  # keep alive

if __name__ == "__main__":
    asyncio.run(main())
