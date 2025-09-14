import os
import socketio
import asyncio
import json
from google import genai

API_Key = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY")
client = genai.Client(api_key=API_Key)

sio = socketio.AsyncClient()
USE_MOCK_AI = True  # flip to False for Gemini

user_colors = ["#FF0000", "#00FF00", "#0000FF"]
user_style = "circles"

def mock_plan(features, colors, style):
    avg = features["avg_energy"]
    dominant_band = max(avg, key=avg.get)

    if dominant_band == "bass":
        shape = "bars"
    elif dominant_band == "drums":
        shape = "radial_lines"
    else:
        shape = "circles"

    return {
        "dominant_band": dominant_band,
        "intensity": "high" if avg[dominant_band] > 0.3 else "low",
        "shapes": style or shape,
        "color_map": colors or ["#FF0000", "#00FF00", "#0000FF"]
    }

async def analyze_song(features, colors, style):
    if USE_MOCK_AI:
        return mock_plan(features, colors, style)

    prompt = f"""
    You are an AI that creates instructions for music-driven visuals.
    Song summary features: {json.dumps(features, indent=2)}
    User colors: {colors}
    User style: {style}
    Output a JSON object with keys: dominant_band, intensity, shapes, color_map.
    """
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return json.loads(response.text)

@sio.event
async def connect():
    print("Connected to server (AI Service)")

@sio.event
async def disconnect():
    print("Disconnected from server (AI Service)")

# Only runs once per song
@sio.on("song_features")
async def on_song_features(data):
    print("Received song features")
    plan = await analyze_song(data, user_colors, user_style)
    print("Visualization plan:", plan)
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
