
from backend.verification.citation_verifier import (
    normalize_text,
    group_documents,
    verify_citations,
)


def sample_document():
    return {
        "title": "AI Basics",
        "file_name": "ai_basics.pdf",
        "page_number": 1,
        "text": (
            "Artificial intelligence systems recognize "
            "patterns, understand language, and make predictions."
        ),
    }


def test_normalize_text_removes_pdf_extension():
    assert normalize_text("AI_Basics.pdf") == "ai basics"


def test_group_documents_combines_chunks_from_same_page():
    documents = [
        {
            **sample_document(),
            "text": "Artificial intelligence recognizes patterns.",
        },
        {
            **sample_document(),
            "text": "AI systems understand language.",
        },
    ]

    grouped = group_documents(documents)

    assert len(grouped) == 1
    assert "recognizes patterns" in grouped[0]["text"]
    assert "understand language" in grouped[0]["text"]


def test_valid_citation_is_verified():
    document = sample_document()
    answer = (
        "Artificial intelligence recognizes patterns and "
        "understands language. "
        "[Source 1: AI Basics, Page 1]"
    )

    verified = verify_citations(answer, [document])

    assert len(verified) == 1
    assert verified[0]["file_name"] == "ai_basics.pdf"
    assert verified[0]["page_number"] == 1


def test_invalid_page_is_rejected():
    document = sample_document()
    answer = (
        "Artificial intelligence recognizes patterns and "
        "understands language. "
        "[Source 1: AI Basics, Page 99]"
    )

    verified = verify_citations(answer, [document])

    assert verified == []


def test_invalid_source_number_is_rejected():
    document = sample_document()
    answer = (
        "Artificial intelligence recognizes patterns and "
        "understands language. "
        "[Source 2: AI Basics, Page 1]"
    )

    verified = verify_citations(answer, [document])

    assert verified == []


def test_empty_answer_returns_no_sources():
    assert verify_citations("", [sample_document()]) == []
