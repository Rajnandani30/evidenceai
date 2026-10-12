
import numpy as np

from backend.retrieval.pdf_hybrid_search import PDFHybridSearch


def sample_chunks():
    return [
        {
            "title": "AI Basics",
            "author": "Test Author",
            "file_name": "ai_basics.pdf",
            "page_number": 1,
            "source": "ai_basics.pdf",
            "text": "Artificial intelligence recognizes patterns and understands language.",
        },
        {
            "title": "Gardening Guide",
            "author": "Test Author",
            "file_name": "gardening.pdf",
            "page_number": 2,
            "source": "gardening.pdf",
            "text": "Gardening containers need drainage holes to prevent excess water.",
        },
        {
            "title": "Machine Learning",
            "author": "Test Author",
            "file_name": "machine_learning.pdf",
            "page_number": 3,
            "source": "machine_learning.pdf",
            "text": "Machine learning models learn patterns from training data.",
        },
    ]


class FakeBM25Search:
    def search(self, query, top_k=5):
        return [
            {"index": 0},
            {"index": 2},
            {"index": 1},
        ][:top_k]


class FakeVectorStore:
    def search(self, query_embedding, top_k=3):
        # Return a deterministic ranking for the three chunks.
        distances = np.array([[0.1, 0.2, 0.3]], dtype="float32")
        indices = np.array([[2, 0, 1]], dtype="int64")
        return distances[:, :top_k], indices[:, :top_k]


def make_search(monkeypatch):
    import backend.retrieval.pdf_hybrid_search as hybrid_module

    # Avoid loading the real embedding model.
    monkeypatch.setattr(
        hybrid_module,
        "generate_embeddings",
        lambda texts: np.ones((len(texts), 3), dtype="float32"),
    )

    search = PDFHybridSearch(sample_chunks())

    # Replace real retrieval components with deterministic test doubles.
    search.bm25_search = FakeBM25Search()
    search.vector_store = FakeVectorStore()

    # Preserve the hybrid ranking order so we can test RRF separately
    # from the cross-encoder model.
    monkeypatch.setattr(
        hybrid_module,
        "rerank",
        lambda query, documents: [
            {**document, "rerank_score": float(document["hybrid_score"])}
            for document in documents
        ],
    )

    return search


def test_hybrid_search_returns_requested_top_k(monkeypatch):
    search = make_search(monkeypatch)

    results = search.search("artificial intelligence", top_k=2)

    assert len(results) == 2


def test_hybrid_search_includes_required_metadata(monkeypatch):
    search = make_search(monkeypatch)

    results = search.search("artificial intelligence", top_k=3)

    for result in results:
        assert "file_name" in result
        assert "page_number" in result
        assert "text" in result
        assert "hybrid_score" in result
        assert "rerank_score" in result


def test_rrf_scores_are_non_negative(monkeypatch):
    search = make_search(monkeypatch)

    results = search.search("artificial intelligence", top_k=3)

    assert all(result["hybrid_score"] >= 0 for result in results)


def test_rrf_combines_bm25_and_vector_ranks(monkeypatch):
    search = make_search(monkeypatch)

    results = search.search(
        "artificial intelligence",
        top_k=3,
        bm25_weight=0.5,
    )

    scores = {
        result["index"]: result["hybrid_score"]
        for result in results
    }

    # Chunk 0 ranks first in BM25 and second in vector search.
    # Chunk 2 ranks second in BM25 and first in vector search.
    # With equal weights, both should receive equal RRF scores.
    assert np.isclose(scores[0], scores[2])


def test_hybrid_search_returns_no_more_than_available_chunks(monkeypatch):
    search = make_search(monkeypatch)

    results = search.search("artificial intelligence", top_k=10)

    assert len(results) == 3
