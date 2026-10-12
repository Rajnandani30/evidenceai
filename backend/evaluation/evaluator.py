from typing import List, Dict, Any
from pathlib import Path
import re


def normalize_text(text: str) -> str:
    """Normalize text for simple answer comparison."""

    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def calculate_retrieval_precision(
    retrieved_chunks: List[Dict[str, Any]],
    relevant_keywords: List[str],
) -> float:
    """
    Calculate the fraction of retrieved chunks containing
    at least one relevant keyword.
    """

    if not retrieved_chunks:
        return 0.0

    relevant_count = 0

    normalized_keywords = [
        normalize_text(keyword)
        for keyword in relevant_keywords
    ]

    for chunk in retrieved_chunks:
        content = normalize_text(
            chunk.get("text", chunk.get("content", ""))
        )

        if any(
            keyword and keyword in content
            for keyword in normalized_keywords
        ):
            relevant_count += 1

    return relevant_count / len(retrieved_chunks)


def calculate_answer_coverage(
    answer: str,
    expected_keywords: List[str],
) -> float:
    """
    Calculate how many expected keywords appear in the answer.
    """

    if not expected_keywords:
        return 0.0

    normalized_answer = normalize_text(answer)

    matched = sum(
        1
        for keyword in expected_keywords
        if normalize_text(keyword) in normalized_answer
    )

    return matched / len(expected_keywords)


def calculate_citation_accuracy(
    answer: str,
    verified_sources: List[Dict[str, Any]],
) -> float:
    """
    Check whether detected citations match verified source
    numbers, filenames/titles, and page numbers.

    This measures citation consistency. It does not independently
    prove that a cited passage supports every factual claim.
    """

    if not answer or not answer.strip():
        return 0.0

    # Match citations such as:
    # [Source 1: second, Page 1]
    # [Source 2: machine_learning.pdf, Page 3]

    citation_pattern = re.compile(
        r"\[\s*Source\s+(\d+)\s*:\s*"
        r"(.*?)\s*,\s*Page\s+(\d+)\s*\]",
        re.IGNORECASE,
    )

    citations = citation_pattern.findall(answer)

    if not citations:
        return 0.0

    # Index sources by their ORIGINAL source numbers.
    # Do not renumber the shortened verified source list.
    verified_by_number = {
        source["source_number"]: source
        for source in verified_sources
        if source.get("source_number") is not None
    }

    verified_count = 0

    for source_number, cited_title, cited_page in citations:

        citation_source_number = int(source_number)
        page_number = int(cited_page)

        source = verified_by_number.get(
            citation_source_number
        )

        # Reject citations that were not verified.
        if source is None:
            continue

        source_title = source.get("title", "")
        source_filename = source.get("file_name", "")

        source_page = source.get("page_number")

        # Accept the title or filename, with or without .pdf.
        valid_names = {
            normalize_text(source_title),
            normalize_text(source_filename),
            normalize_text(
                Path(source_filename).stem
            ) if source_filename else "",
            normalize_text(
                Path(source_title).stem
            ) if source_title else "",
        }

        valid_names.discard("")

        cited_name = normalize_text(cited_title)

        # Validate both the source name and page number.
        if (
            cited_name in valid_names
            and source_page is not None
            and int(source_page) == page_number
        ):
            verified_count += 1

    return verified_count / len(citations)


def evaluate_response(
    question: str,
    answer: str,
    retrieved_chunks: List[Dict[str, Any]],
    verified_sources: List[Dict[str, Any]],
    expected_keywords: List[str],
    relevant_keywords: List[str],
    response_time: float,
) -> Dict[str, Any]:
    """Evaluate one EvidenceAI response."""

    retrieval_precision = calculate_retrieval_precision(
        retrieved_chunks,
        relevant_keywords,
    )

    answer_coverage = calculate_answer_coverage(
        answer,
        expected_keywords,
    )

    citation_accuracy = calculate_citation_accuracy(
        answer,
        verified_sources,
    )

    return {
        "question": question,
        "retrieval_precision": round(
            retrieval_precision, 3
        ),
        "answer_coverage": round(
            answer_coverage, 3
        ),
        "citation_accuracy": round(
            citation_accuracy, 3
        ),
        "response_time_seconds": round(
            response_time, 3
        ),
    }
