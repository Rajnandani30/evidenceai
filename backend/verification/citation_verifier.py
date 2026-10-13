
import re


def normalize_text(text):
    """Normalize filenames and titles for comparison."""
    text = str(text or "").lower().strip()
    text = re.sub(r"\.pdf$", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def group_documents(documents):
    """
    Group retrieved chunks by filename and page number.
    Preserve source ordering to match prompt_builder.py.
    """
    grouped_sources = {}

    for document in documents:
        file_name = document.get("file_name", "")
        page_number = document.get("page_number")
        title = document.get("title") or file_name

        source_key = (file_name.lower(), page_number)

        if source_key not in grouped_sources:
            grouped_sources[source_key] = {
                "title": title,
                "file_name": file_name,
                "page_number": page_number,
                "texts": [],
            }

        text = document.get("text", "").strip()
        if text:
            grouped_sources[source_key]["texts"].append(text)

    sources = []

    for source_number, source in enumerate(
        grouped_sources.values(), start=1
    ):
        sources.append({
            "source_number": source_number,
            "title": source["title"],
            "file_name": source["file_name"],
            "page_number": source["page_number"],
            "text": "\n\n".join(source["texts"]),
        })

    return sources


def verify_citations(answer, documents):
    """
    Check citation format, source number, filename/title, page,
    and basic lexical overlap with the cited evidence.

    Lexical overlap is only a heuristic; it does not prove
    that the source semantically supports the claim.
    """
    verified_sources = []

    if not answer or not documents:
        return verified_sources

    sources = group_documents(documents)

    citation_pattern = re.compile(
        r"\[\s*Source\s+(\d+)\s*:\s*"
        r"(.*?)\s*,\s*Page\s+(\d+)\s*\]",
        re.IGNORECASE,
    )

    citations = citation_pattern.finditer(answer)

    for citation in citations:
        source_number_text, source_name, page_number_text = (
            citation.groups()
        )

        source_number = int(source_number_text)
        source_index = source_number - 1

        if not 0 <= source_index < len(sources):
            continue

        source = sources[source_index]

        cited_name = normalize_text(source_name)
        valid_names = {
            normalize_text(source.get("title")),
            normalize_text(source.get("file_name")),
        }
        valid_names.discard("")

        if cited_name not in valid_names:
            continue

        actual_page = source.get("page_number")
        if actual_page is None:
            continue

        try:
            if int(page_number_text) != int(actual_page):
                continue
        except (TypeError, ValueError):
            continue

        # Extract the sentence immediately before this citation.
        text_before_citation = answer[:citation.start()]
        sentences = [
            sentence.strip().lower()
            for sentence in re.split(
                r"[.!?\n]+", text_before_citation
            )
            if sentence.strip()
        ]

        claim = sentences[-1] if sentences else ""

        claim_words = set(
            re.findall(r"\b[a-zA-Z]{4,}\b", claim)
        )
        source_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                source.get("text", "").lower(),
            )
        )

        common_words = claim_words.intersection(source_words)

        # Require at least two shared words.
        if len(common_words) < 2:
            continue

        verified_source = {
            "source_number": source["source_number"],
            "file_name": source.get("file_name"),
        }

        if source.get("title"):
            verified_source["title"] = source["title"]

        if actual_page is not None:
            verified_source["page_number"] = actual_page

        if verified_source not in verified_sources:
            verified_sources.append(verified_source)

    return verified_sources
