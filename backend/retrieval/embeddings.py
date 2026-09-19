from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(texts):
    embeddings = model.encode(texts)

    return embeddings


if __name__ == "__main__":
    sample_texts = [
        "Artificial Intelligence is a field of computer science.",
        "Machine Learning allows computers to learn from data.",
    ]

    embeddings = generate_embeddings(sample_texts)

    print("Number of texts:", len(sample_texts))
    print("Embedding shape:", embeddings.shape)