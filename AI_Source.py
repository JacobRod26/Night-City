import socketio
import asyncio
import json

sio = socketio.AsyncClient()
USE_MOCK_AI = True

user_colors = ["#ff5733", "#33c1ff", "#90ee90"]
user_style = "radial_lines"

def mock_plan(bands, colors, style):
    dominant_band = max(bands, key=bands.get)
    return {
        "dominant_band": dominant_band,
        "intensity": "high" if bands[dominant_band] > 0.3 else "low",
        "shapes": style,
        "color_map": colors
    }

@sio.event
async def connect():
    print("Connected to server (AI Service)")

@sio.event
async def disconnect():
    print("Disconnected (AI Service)")

@sio.on("eq_data")
async def on_eq_data(data):
    global user_colors, user_style
    bands = data.get("bands", {})
    if not bands: return
    plan = mock_plan(bands, user_colors, user_style)
    await sio.emit("ai_instructions", plan)

@sio.on("user_input")
async def on_user_input(data):
    global user_colors, user_style
    user_colors = data.get("colors", user_colors)
    user_style = data.get("style", user_style)
    print("Updated user settings:", user_colors, user_style)

async def main():
    await sio.connect("http://localhost:8000")
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())
