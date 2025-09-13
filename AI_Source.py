import os
from google import genai

API_Key = os.getenv("GOOGLE_API_KEY", "AIzaSyCNHY3ngXuDhsnbEe40euScYuePzMfi_HM")  #put your API key in the quotes

client = genai.Client(api_key = API_Key)

def analyze_audio(bands: list[float], colors: list[str]) -> str:
    """
    Ask Gemini to analyze audio band data and suggest visualization parameters
    """
    
    prompt = f"""
    You are an AI that creates instructions for music-driven visuals.
    - Input: 32-band spectrum values (energy in each band).
    - Colors chosen by the user: {colors}.
    - Output: A JSON object describing how to visualize the music. Include things like which bands dominate, movement style, shapes, or intensity.
    Spectrum values: {bands}
    """

    response = client.models.generate_content(
        model = "gemini-1.5-flash",\
        contents = prompt
    )
    return response.text



