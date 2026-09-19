from backend.ingestion.loader import load_documents
from backend.retrieval.bm25_search import BM25Search
from backend.retrieval.embeddings import generate_embeddings
from backend.retrieval.vector_store import VectorStore


class HybridSearch:
    def __init__(self, documents):
        self.documents = documents

        # BM25 keyword search
        self.bm25_search = BM25Search(documents)

        # Generate embeddings for all documents
        document_texts = [document["text"] for document in documents]
        embeddings = generate_embeddings(document_texts)

        # Create FAISS vector store
        self.vector_store = VectorStore(
            dimension=embeddings.shape[1]
        )

        self.vector_store.add_embeddings(embeddings)

    def search(self, query, top_k=3):
        # BM25 search
        bm25_results = self.bm25_search.search(
            query,
            top_k=top_k
        )

        # Convert query into an embedding
        query_embedding = generate_embeddings([query])

        # FAISS search
        distances, indices = self.vector_store.search(
            query_embedding,
            top_k=top_k
        )

        results = {
            "bm25": bm25_results,
            "vector": []
        }

        # Store FAISS results
        for distance, index in zip(
            distances[0],
            indices[0]
        ):
            results["vector"].append(
                {
                    "index": int(index),
                    "distance": float(distance),
                    "file_name": self.documents[index]["file_name"],
                    "text": self.documents[index]["text"],
                }
            )

        return results


if __name__ == "__main__":
    documents = load_documents("data/sample_documents")

    search_engine = HybridSearch(documents)

    results = search_engine.search(
        "What is Machine Learning?",
        top_k=2
    )

    print("\n=== BM25 RESULTS ===")

    for result in results["bm25"]:
        print("\nFile:", result["file_name"])
        print("Score:", result["score"])

    print("\n=== VECTOR RESULTS ===")

    for result in results["vector"]:
        print("\nFile:", result["file_name"])
        print("Distance:", result["distance"])