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