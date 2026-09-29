from backend.ingestion.pdf_ingest import ingest_pdf
from backend.retrieval.pdf_bm25_search import PDFBM25Search
from backend.retrieval.embeddings import generate_embeddings
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.reranker import rerank


class PDFHybridSearch:

    def __init__(self, chunks):

        self.chunks = chunks

        # -------------------------
        # BM25 Search
        # -------------------------

        self.bm25_search = PDFBM25Search(chunks)

        # -------------------------
        # Vector Search
        # -------------------------

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = generate_embeddings(texts)

        self.vector_store = VectorStore(
            dimension=embeddings.shape[1]
        )

        self.vector_store.add_embeddings(
            embeddings
        )

    def search(
        self,
        query,
        top_k=5,
        bm25_weight=0.5
    ):

        # -------------------------
        # 1. BM25 Ranking
        # -------------------------

        bm25_results = self.bm25_search.search(
            query,
            top_k=len(self.chunks)
        )

        bm25_ranks = {}

        for rank, result in enumerate(
            bm25_results,
            start=1
        ):

            bm25_ranks[result["index"]] = rank

        # -------------------------
        # 2. Vector Search Ranking
        # -------------------------

        query_embedding = generate_embeddings(
            [query]
        )

        distances, indices = self.vector_store.search(
            query_embedding,
            top_k=len(self.chunks)
        )

        vector_ranks = {}

        for rank, index in enumerate(
            indices[0],
            start=1
        ):

            index = int(index)

            if 0 <= index < len(self.chunks):

                vector_ranks[index] = rank

        # -------------------------
        # 3. Reciprocal Rank Fusion
        # -------------------------

        rrf_k = 60

        hybrid_results = []

        for index in range(len(self.chunks)):

            bm25_rank = bm25_ranks.get(index)

            vector_rank = vector_ranks.get(index)

            bm25_score = (
                bm25_weight / (rrf_k + bm25_rank)
                if bm25_rank is not None
                else 0.0
            )

            vector_score = (
                (1 - bm25_weight)
                / (rrf_k + vector_rank)
                if vector_rank is not None
                else 0.0
            )

            hybrid_score = (
                bm25_score + vector_score
            )

            chunk = self.chunks[index]

            hybrid_results.append({

                "index": index,

                # PDF metadata
                "title": chunk["title"],
                "author": chunk["author"],
                "file_name": chunk["file_name"],
                "page_number": chunk["page_number"],
                "source": chunk["source"],

                # Evidence text
                "text": chunk["text"],

                # Retrieval scores
                "bm25_score": bm25_score,
                "vector_score": vector_score,
                "hybrid_score": hybrid_score,

                # Ranking information
                "bm25_rank": bm25_rank,
                "vector_rank": vector_rank,

            })

        hybrid_results.sort(
            key=lambda result: result["hybrid_score"],
            reverse=True
        )

        # -------------------------
        # 4. Cross-Encoder Reranking
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

    search_engine = PDFHybridSearch(chunks)

    results = search_engine.search(
        "retrieval augmented generation",
        top_k=5
    )

    print(
        "PDF HYBRID SEARCH + RRF + RERANKING RESULTS:"
    )

    for result in results:

        print(f"\nTitle: {result['title']}")
        print(f"Author: {result['author']}")
        print(f"Page: {result['page_number']}")
        print(f"Source: {result['source']}")

        print(
            f"BM25 Rank: {result['bm25_rank']}"
        )

        print(
            f"Vector Rank: {result['vector_rank']}"
        )

        print(
            f"RRF Score: {result['hybrid_score']:.6f}"
        )

        print(
            f"Rerank Score: {result['rerank_score']:.4f}"
        )

        print(
            f"Text: {result['text'][:250]}..."
        )