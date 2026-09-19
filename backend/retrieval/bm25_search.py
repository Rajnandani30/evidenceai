from rank_bm25 import BM25Okapi
from backend.ingestion.loader import load_documents


class BM25Search:
    def __init__(self, documents):
        self.documents = documents

        tokenized_documents = [
            document["text"].lower().split()
            for document in documents
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

    def search(self, query, top_k=3):
        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indices[:top_k]:
            results.append(
                {
                    "index": index,
                    "score": float(scores[index]),
                    "file_name": self.documents[index]["file_name"],
                    "text": self.documents[index]["text"],
                }
            )

        return results


if __name__ == "__main__":
    documents = load_documents("data/sample_documents")

    search_engine = BM25Search(documents)

    results = search_engine.search(
        "Machine Learning",
        top_k=2
    )

    for result in results:
        print("\nFile:", result["file_name"])
        print("Score:", result["score"])
        print("Text:", result["text"])