from backend.ingestion.pdf_ingest import ingest_pdf
from backend.retrieval.pdf_bm25_search import PDFBM25Search
from backend.retrieval.embeddings import generate_embeddings
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.scoring import normalize_scores
from backend.retrieval.reranker import rerank


class PDFHybridSearch:

    def __init__(self, chunks):

        self.chunks = chunks

        # BM25 search
        self.bm25_search = PDFBM25Search(chunks)

        # Vector search
        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        self.vector_store = VectorStore(
            dimension=embeddings.shape[1]
        )

        self.vector_store.add_embeddings(embeddings)

    def search(self, query, top_k=5, bm25_weight=0.5):

        # -------------------------
        # BM25 Search
        # -------------------------

        bm25_results = self.bm25_search.search(
            query,
            top_k=len(self.chunks)
        )

        bm25_scores = [
            result["score"]
            for result in bm25_results
        ]

        normalized_bm25 = normalize_scores(
            bm25_scores
        )

        bm25_lookup = {}

        for result, score in zip(
            bm25_results,
            normalized_bm25
        ):

            bm25_lookup[result["index"]] = score

        # -------------------------
        # Vector Search
        # -------------------------

        query_embedding = generate_embeddings(
            [query]
        )

        distances, indices = self.vector_store.search(
            query_embedding,
            top_k=len(self.chunks)
        )

        vector_distances = list(
            distances[0]
        )

        normalized_vector = normalize_scores(
            vector_distances,
            reverse=True
        )

        vector_lookup = {}

        for index, score in zip(
            indices[0],
            normalized_vector
        ):

            vector_lookup[int(index)] = score

        # -------------------------
        # Combine Scores
        # -------------------------

        hybrid_results = []

        for index in range(len(self.chunks)):

            bm25_score = bm25_lookup.get(
                index,
                0.0
            )

            vector_score = vector_lookup.get(
                index,
                0.0
            )

            hybrid_score = (
                bm25_weight * bm25_score
                +
                (1 - bm25_weight) * vector_score
            )

            hybrid_results.append(
                {
                    "index": index,
                    "file_name": self.chunks[index]["file_name"],
                    "page_number": self.chunks[index]["page_number"],
                    "text": self.chunks[index]["text"],
                    "bm25_score": bm25_score,
                    "vector_score": vector_score,
                    "hybrid_score": hybrid_score,
                }
            )

        hybrid_results.sort(
            key=lambda result: result["hybrid_score"],
            reverse=True
        )

        # -------------------------
        # Cross-Encoder Reranking
        # -------------------------

        candidates = hybrid_results[:top_k]

        reranked_results = rerank(
            query,
            candidates
        )

        return reranked_results


if __name__ == "__main__":

    pdf_path = "data/pdf_documents/sample.pdf"

    chunks = ingest_pdf(pdf_path)

    search_engine = PDFHybridSearch(
        chunks
    )

    results = search_engine.search(
        "retrieval augmented generation",
        top_k=5
    )

    print("PDF HYBRID SEARCH + RERANKING RESULTS:")

    for result in results:

        print(
            f"\nPage: {result['page_number']}"
        )

        print(
            f"BM25 Score: {result['bm25_score']:.4f}"
        )

        print(
            f"Vector Score: {result['vector_score']:.4f}"
        )

        print(
            f"Hybrid Score: {result['hybrid_score']:.4f}"
        )

        print(
            f"Rerank Score: {result['rerank_score']:.4f}"
        )

        print(
            f"Text: {result['text'][:250]}..."
        )