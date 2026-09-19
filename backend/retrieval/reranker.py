from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

model = CrossEncoder(MODEL_NAME)


def rerank(query, documents):
    pairs = [
        [query, document["text"]]
        for document in documents
    ]

    scores = model.predict(pairs)

    ranked_documents = []

    for document, score in zip(documents, scores):
        result = document.copy()
        result["rerank_score"] = float(score)
        ranked_documents.append(result)

    ranked_documents.sort(
        key=lambda document: document["rerank_score"],
        reverse=True
    )

    return ranked_documents


if __name__ == "__main__":
    query = "What is Machine Learning?"

    documents = [
        {
            "file_name": "ai_basics.txt",
            "text": "Artificial Intelligence is a field of computer science."
        },
        {
            "file_name": "machine_learning.txt",
            "text": "Machine Learning allows computers to learn patterns from data."
        },
        {
            "file_name": "deep_learning.txt",
            "text": "Deep Learning uses neural networks to learn complex patterns."
        },
    ]

    results = rerank(query, documents)

    print("\n=== RERANKED RESULTS ===")

    for result in results:
        print("\nFile:", result["file_name"])
        print("Rerank Score:", result["rerank_score"])
        print("Text:", result["text"])