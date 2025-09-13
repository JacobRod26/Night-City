import os
from google import genai

API_Key = os.getenv("GOOGLE_API_KEY", "")  #put your API key in the quotes

client = genai.Client(api_key = API_KEY)

def ask_gemini(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Send a text prompt to Google AI and return the response.
    """
    response = client.models.generate_content(
        model = model,
        contents = prompt
    )

    return response.text


SYSTEM_PROMPTS = """You are an AI assistant.
Answer clearly and concisely.
"""

HELLO_PROMPT = "Explain how AI works in simple words."

def main():
    print("Starting AI project.....\n")

    response = ask_gemini(HELLO_PROMPT)
    print("AI Response:", response)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            print("See ya!")
            break
        reply = ask_gemini(user_input)

if __name__ == "__main__":
    main()
