import os
import asyncio
import socketio
import json
from google import genai

SIO_URL = "http://localhost8000"
API_Key = os.getenv("GOOGLE_API_KEY", "")  #put your API key in the quotes
client = genai.Client(api_key = API_Key)

sio = socketio.AsyncClient()

latest_user = {"colors": ["#FF5733", "#33C1FF", "#90EE90"]}
latest_bands = [0.0]*32

def analyze_audio(bands: list[float], colors: list[str]) -> str:
    """
    Ask Gemini to analyze audio band data and suggest visualization parameters
    """
    
    prompt = f"""
    You are an AI that creates instructions for music-driven visuals.
    - Input: 32-band spectrum values (energy in each band).
    - Colors chosen by the user: {colors}.
    - Output: A JSON object describing how to visualize the music. Include things like which bands dominate, movement style, shapes, or intensity(e.g. "dominant_band": "bass", "intensity": "high", "shapes": "radial_lines", "color_map": ["#FF0000", "#00FF00", "#0000FF"]).
    Spectrum values: {bands}
    """

    response = client.models.generate_content(
        model = "gemini-1.5-flash",\
        contents = prompt
    )
    return response.text

@sio.event
async def connect():
    print("AI service conntected to server.")

@sio.event
async def disconnected():
    print("AI service disconnected from server.")

@sio.event
async def user_input(data):
    global latest_user
    latest_user = data
    print("Updated user input:", latest_user)

@sio.event
async def eq_data(data):
    global latest_bands
    latest_bands = data.get("bands", [0.0]*32)

    try:
        result = analyze_audio(latest_bands, latest_user.get("colors", []))

        try:
            parsed = json.loads(result)
            await sio.emit("ai_instructions", parsed)
        except Exception:
            await sio.emit("ai_instructions", {"raw":result})

        print("AI output sent.")
    except Exception as e:
        print("AI error:", e)


async def main()
    await sio.conect(SIO_URL)
    await sio.wait()

if __name__ == "__main__":

    asyncio.run(main())
