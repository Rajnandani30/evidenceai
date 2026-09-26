
import re


def normalize_text(text):
    """Normalize filenames and titles for comparison."""

    text = str(text or "").lower().strip()

    text = re.sub(r"\.pdf$", "", text)

    text = re.sub(r"[^a-z0-9]+", " ", text)

    return " ".join(text.split())


def group_documents(documents):
    """
    Group retrieved chunks using the same
    filename and page-number logic as prompt_builder.py.
    """

    grouped_sources = {}

    for document in documents:

        file_name = document.get("file_name", "")
        page_number = document.get("page_number")
        title = document.get("title") or file_name

        source_key = (
            file_name.lower(),
            page_number
        )

        if source_key not in grouped_sources:

            grouped_sources[source_key] = {
                "title": title,
                "file_name": file_name,
                "page_number": page_number,
                "texts": []
            }

        text = document.get("text", "").strip()

        if text:
            grouped_sources[source_key]["texts"].append(text)

    # Preserve the insertion order.
    # This must match the order in prompt_builder.py.

    sources = []

    for source in grouped_sources.values():

        combined_text = "\n\n".join(
            source["texts"]
        )

        sources.append({
            "title": source["title"],
            "file_name": source["file_name"],
            "page_number": source["page_number"],
            "text": combined_text
        })

    return sources


def verify_citations(answer, documents):

    verified_sources = []

    if not answer or not documents:
        return verified_sources

    # Recreate the exact source list shown to Gemini.

    sources = group_documents(documents)

    # Supports citations such as:
    # [Source 1: second.pdf, Page 1]
    # [Source 1: The Solar System: A Basic Guide, Page 1]
    #
    # Also supports multiple sources inside one bracket:
    # [Source 1: Example, Page 1; Source 2: Example, Page 2]

    citation_pattern = re.compile(
        r"\[\s*Source\s+(\d+)\s*:\s*"
        r"(.*?)"
        r"(?:\s*,\s*Page\s+(\d+))?"
        r"\s*(?=;|\])",
        re.IGNORECASE
    )

    citations = citation_pattern.findall(answer)

    # Remove citations before checking evidence overlap.

    answer_without_citations = re.sub(
        r"\[\s*Source\s+\d+\s*:.*?\]",
        "",
        answer,
        flags=re.IGNORECASE
    ).lower()

    answer_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            answer_without_citations
        )
    )

    for source_number, source_name, page_number in citations:

        source_index = int(source_number) - 1

        # Check that the source number exists.

        if source_index < 0 or source_index >= len(sources):
            continue

        source = sources[source_index]

        # Validate the source title or filename.

        cited_name = normalize_text(source_name)

        valid_names = {
            normalize_text(source.get("title")),
            normalize_text(source.get("file_name"))
        }

        valid_names.discard("")

        if cited_name not in valid_names:
            continue

        # Validate the page number.

        if page_number:

            actual_page = source.get("page_number")

            if actual_page is None:
                continue

            if int(page_number) != int(actual_page):
                continue

        # Check whether the answer has meaningful
        # word overlap with the cited evidence.

        source_text = source.get(
            "text",
            ""
        ).lower()

        source_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                source_text
            )
        )

        common_words = source_words.intersection(
            answer_words
        )

        if len(common_words) < 2:
            continue

        # Add the verified source.

        verified_source = {
            "file_name": source.get("file_name")
        }

        if source.get("title"):
            verified_source["title"] = source["title"]

        if source.get("page_number") is not None:
            verified_source["page_number"] = (
                source["page_number"]
            )

        # Avoid duplicate entries.

        if verified_source not in verified_sources:
            verified_sources.append(verified_source)

    return verified_sources