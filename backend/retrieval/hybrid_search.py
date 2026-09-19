from backend.ingestion.loader import load_documents
from backend.retrieval.bm25_search import BM25Search
from backend.retrieval.embeddings import generate_embeddings
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.scoring import normalize_scores


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

    def search(self, query, top_k=3, bm25_weight=0.5):
        # BM25 search
        bm25_results = self.bm25_search.search(
            query,
            top_k=len(self.documents)
        )

        # Query embedding
        query_embedding = generate_embeddings([query])

        # FAISS search
        distances, indices = self.vector_store.search(
            query_embedding,
            top_k=len(self.documents)
        )

        # Normalize BM25 scores
        bm25_scores = [
            result["score"]
            for result in bm25_results
        ]

        normalized_bm25 = normalize_scores(bm25_scores)

        # Normalize FAISS distances
        vector_distances = list(distances[0])

        normalized_vector = normalize_scores(
            vector_distances,
            reverse=True
        )

        # Create score lookup dictionaries
        bm25_lookup = {}

        for result, score in zip(
            bm25_results,
            normalized_bm25
        ):
            bm25_lookup[result["index"]] = score

        vector_lookup = {}

        for index, score in zip(
            indices[0],
            normalized_vector
        ):
            vector_lookup[int(index)] = score

        # Calculate hybrid scores
        hybrid_results = []

        for index in range(len(self.documents)):
            bm25_score = bm25_lookup.get(index, 0.0)
            vector_score = vector_lookup.get(index, 0.0)

            hybrid_score = (
                bm25_weight * bm25_score
                + (1 - bm25_weight) * vector_score
            )

            hybrid_results.append(
                {
                    "index": index,
                    "file_name": self.documents[index]["file_name"],
                    "text": self.documents[index]["text"],
                    "bm25_score": bm25_score,
                    "vector_score": vector_score,
                    "hybrid_score": hybrid_score,
                }
            )

        # Sort by hybrid score
        hybrid_results.sort(
            key=lambda result: result["hybrid_score"],
            reverse=True
        )

        return hybrid_results[:top_k]


if __name__ == "__main__":
    documents = load_documents("data/sample_documents")

    search_engine = HybridSearch(documents)

    results = search_engine.search(
        "What is Machine Learning?",
        top_k=2
    )

    print("\n=== HYBRID SEARCH RESULTS ===")

    for result in results:
        print("\nFile:", result["file_name"])
        print("BM25 Score:", result["bm25_score"])
        print("Vector Score:", result["vector_score"])
        print("Hybrid Score:", result["hybrid_score"])