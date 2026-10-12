from rank_bm25 import BM25Okapi
from backend.ingestion.pdf_ingest import ingest_pdf


class PDFBM25Search:

    def __init__(self, chunks):
        self.chunks = chunks
        self.bm25 = None

        if not self.chunks:
            return

        tokenized_chunks = [
            chunk["text"].lower().split()
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(tokenized_chunks)

    def search(self, query, top_k=5):
        """
        Return keyword-matched chunks ranked by BM25.
        Ignore chunks with non-positive BM25 scores so
        unmatched documents do not receive artificial ranks.
        """

        if not self.chunks or top_k <= 0:
            return []

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        for index in ranked_indices:

            score = float(scores[index])

            # Do not rank chunks that have no positive BM25 score.
            if score <= 0:
                continue

            results.append({
                "index": index,
                "score": score,
                "file_name": self.chunks[index]["file_name"],
                "page_number": self.chunks[index]["page_number"],
                "text": self.chunks[index]["text"],
            })

            if len(results) >= top_k:
                break

        return results


if __name__ == "__main__":

    pdf_path = "data/pdf_documents/sample.pdf"

    chunks = ingest_pdf(pdf_path)

    search_engine = PDFBM25Search(chunks)

    results = search_engine.search(
        "retrieval augmented generation",
        top_k=5
    )

    print("PDF BM25 Search Results:")

    for result in results:
        print(f"\nScore: {result['score']:.4f}")
        print(f"Page: {result['page_number']}")
        print(f"File: {result['file_name']}")
        print(f"Text: {result['text'][:300]}...")
