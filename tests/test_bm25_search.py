
from backend.retrieval.pdf_bm25_search import PDFBM25Search


def sample_chunks():
    return [
        {
            "file_name": "ai_basics.pdf",
            "page_number": 1,
            "text": (
                "Artificial intelligence systems recognize "
                "patterns and understand language."
            ),
        },
        {
            "file_name": "gardening.pdf",
            "page_number": 2,
            "text": (
                "Gardening containers need drainage holes "
                "to prevent excess water."
            ),
        },
        {
            "file_name": "machine_learning.pdf",
            "page_number": 3,
            "text": (
                "Machine learning models learn patterns "
                "from training data."
            ),
        },
    ]


def test_bm25_finds_relevant_document():
    search = PDFBM25Search(sample_chunks())

    results = search.search("artificial intelligence language", top_k=3)

    assert len(results) == 3
    assert results[0]["file_name"] == "ai_basics.pdf"


def test_bm25_respects_top_k():
    search = PDFBM25Search(sample_chunks())

    results = search.search("patterns", top_k=2)

    assert len(results) == 2


def test_bm25_returns_document_metadata():
    search = PDFBM25Search(sample_chunks())

    results = search.search("gardening drainage", top_k=1)

    assert results[0]["file_name"] == "gardening.pdf"
    assert results[0]["page_number"] == 2
    assert "text" in results[0]
    assert "score" in results[0]


def test_bm25_handles_empty_collection():
    search = PDFBM25Search([])

    results = search.search("artificial intelligence", top_k=5)

    assert results == []
