import os

from dotenv import load_dotenv
from google import genai

from backend.generation.prompt_builder import build_rag_prompt
from backend.verification.citation_verifier import verify_citations


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


MODEL_NAME = "gemini-flash-lite-latest"


def generate_answer(query, documents):

    prompt = build_rag_prompt(
        query,
        documents
    )

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text

    except Exception as error:

        error_message = str(error)

        if "503" in error_message:

            answer = (
                "Gemini is temporarily unavailable because "
                "the model is experiencing high demand. "
                "Please try again later."
            )

        else:

            raise

    verified_sources = verify_citations(
        answer,
        documents
    )

    return answer, verified_sources


if __name__ == "__main__":

    sample_documents = [
        {
            "file_name": "machine_learning.txt",
            "text": (
                "Machine Learning allows computers "
                "to learn patterns from data."
            )
        },
        {
            "file_name": "ai_basics.txt",
            "text": (
                "Artificial Intelligence is a field "
                "of computer science."
            )
        },
    ]

    answer, verified_sources = generate_answer(
        "What is Machine Learning?",
        sample_documents
    )

    print("EvidenceAI Answer:")
    print(answer)

    print("\nVerified Sources:")

    for source in verified_sources:
        print("-", source)