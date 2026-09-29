
from typing import List, Dict, Any
from pathlib import Path
import re


def normalize_text(text: str) -> str:
    """Normalize text for simple answer comparison."""

    text = text.lower()
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
    Check whether citations in the answer match the
    filename/title and page number of verified sources.

    Returns the fraction of detected citations that match
    a verified source and its page.

    This is a citation consistency metric. It does not
    independently prove that the cited text supports
    every factual claim.
    """

    if not answer.strip() or not verified_sources:
        return 0.0

    # Matches citations such as:
    # [Source 1: second, Page 1]
    # [Source 2: machine_learning.pdf, Page 3]

    citation_pattern = (
        r"\[Source\s+(\d+)\s*:\s*"
        r"(.*?),\s*Page\s*(\d+)\]"
    )

    citations = re.findall(
        citation_pattern,
        answer,
        flags=re.IGNORECASE,
    )

    if not citations:
        return 0.0

    verified_count = 0

    for source_number, cited_title, cited_page in citations:

        source_index = int(source_number) - 1
        page_number = int(cited_page)

        # Check that the citation refers to an existing
        # verified source.
        if not (
            0 <= source_index < len(verified_sources)
        ):
            continue

        source = verified_sources[source_index]

        # Read the actual verified source metadata.
        source_title = source.get("title", "")

        source_filename = source.get("file_name", "")

        source_page = source.get("page_number")

        # Support citations using either the PDF title
        # or the filename, with or without .pdf.
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

        cited_name = normalize_text(cited_title)

        # Check both the source name and page number.
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