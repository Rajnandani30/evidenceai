import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


MODEL_NAME = "gemini-3.6-flash"


def generate_answer(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    answer = generate_answer(
        "Explain Artificial Intelligence in one simple sentence."
    )

    print("LLM Response:")
    print(answer)