import socketio
import asyncio
import json
import os
from google import genai

sio = socketio.AsyncClient()

USE_MOCK_AI = True #flip to false when ready to use gemini

API_KEY = os.getenv("GOOGLE_API_KEY", "")#API Key Here!!!!
client = genai.Client(api_key=API_KEY)

user_colors = ["#ff5733", "#33c1ff", "#90ee90"]
user_style = "radial_lines"

gemini_plan = None #cache so we only call Gemini once per song

#this is for the mock AI
def mock_plan(bands, colors, style):
    dominant_band = max(bands, key=bands.get)
    return {
        "dominant_band": dominant_band,
        "intensity": "high" if bands[dominant_band] > 0.3 else "low",
        "shapes": style,
        "color_map": colors
    }


#this is for Gemini
def gemini_analyze(bands, colors, style):
    """
    Ask Gemini once per song. 
    We don't stream every chunk.
    """
    prompt = f"""
    You are an AI that creates instructions for music-driven visuals.
    Input spectrum snapshot: {bands}
    Colors chosen: {colors}
    Style: {style}
    Output ONLY JSON, like:
    {{
      "dominant_band": "...",
      "intensity": "...",
      "shapes": "...",
      "color_map": [...]
    }}
    """
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    try:
        return json.loads(response.text)
    except Exception:
        # fallback to mock if Gemini fails
        return mock_plan(bands, colors, style)


@sio.event
async def connect():
    print("Connected to server (AI Service)")

@sio.event
async def disconnect():
    print("Disconnected (AI Service)")

@sio.on("eq_data")
async def on_eq_data(data):
    global gemini_plan
    bands = data.get("bands", {})
    if not bands: 
        return
    
    if USE_MOCK_AI:
        #continous updates
        plan = mock_plan(bands, user_colors, user_style)
        await sio.emit("ai_instructions", plan)
    else:
        #Gemini: only once, then reuse
        if gemini_plan is None:
            gemini_plan = gemini_analyze(bands, user_colors, user_style)
            print("Gemini plan computed:", gemini_plan)
            await sio.emit("ai_instructions", gemini_plan)
        else:
            #reuse cached plan
            await sio.emit("ai_instructions", gemini_plan)


@sio.on("user_input")
async def on_user_input(data):
    global user_colors, user_style, gemini_plan
    user_colors = data.get("colors", user_colors)
    user_style = data.get("style", user_style)
    gemini_plan = None #reset the cache at a new song input
    print("Updated user settings:", user_colors, user_style)

async def main():
    await sio.connect("http://localhost:8000")
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())
