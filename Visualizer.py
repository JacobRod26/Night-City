import socketio
import asyncio
import base64
import io
import json
import pygame
import math
from PIL import Image
import random

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

def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB colors."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

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
        if intensity == "high":
            num_lines = 15
            length_boost = 24  # 8 * 3
        elif intensity == "medium":
            num_lines = 11
            length_boost = 16  # 8 * 2
        else:
            num_lines = 7
            length_boost = 8   # 8 * 1
        for i in range(num_lines):
            angle = (i / num_lines) * 360
            rad = angle * math.pi / 180
            col = random.choice(colors)
            rand_length = random.randint(32, 124) + length_boost
            x = int(cx + rand_length * math.cos(rad))
            y = int(cy + rand_length * math.sin(rad))
            pygame.draw.line(screen, col, (cx, cy), (x, y), 6)

    elif shape == "circles":
        t = pygame.time.get_ticks() * 0.001  # time animation
        for i in range(1, len(colors) + 1):
            c1 = colors[i % len(colors)]
            c2 = colors[(i + 1) % len(colors)]
            col = lerp_color(c1, c2, (math.sin(t + i) + 1) / 2)
            radius = int(level * i / len(colors)) + 30
            pygame.draw.circle(screen, col, (cx, cy), radius, 3)

    elif shape == "bars":
        total_bars = len(colors)
        bar_spacing = 20  # space between bars
        total_spacing = bar_spacing * (total_bars - 1)
        max_bar_width = 200  # or any max width you want per bar
        total_bars_width = total_bars * max_bar_width + total_spacing

        start_x = (WIDTH - total_bars_width) // 2

        for i, col in enumerate(colors):
            bar_height = 300 + int(level * (i + 1) / len(colors))
            x = start_x + i * (max_bar_width + bar_spacing)
            pygame.draw.rect(screen, col, (x, HEIGHT - bar_height, max_bar_width, bar_height))

    elif shape == "waves":
        mid_y = HEIGHT // 2
        points = []
        t = pygame.time.get_ticks() * 0.005

        eq_items = list(eq_data.items())
        for i, (band, value) in enumerate(eq_items):
            x = int((i / max (1, len(eq_items) - 1)) * WIDTH)
            amp = value * (200 if intensity == "high" else 100)
            y = mid_y + int(math.sin(i * 0.5 + t) * amp)
            points.append((x,y))
        if len(points) > 1:
            for i in range(len(points) - 1):
                segment_t = i / (len(points) - 1)
                c1 = colors[int(segment_t * (len(colors)-1))]
                c2 = colors[min(len(colors) - 1, int(segment_t * (len(colors) - 1)) + 1)]
                seg_color = lerp_color(c1,c2, (segment_t * (len(colors) - 1)) % 1)
                pygame.draw.line(screen, seg_color, points[i], points[i+1], 6)

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
