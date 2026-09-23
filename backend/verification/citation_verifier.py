import re


def verify_citations(answer, documents):

    verified_sources = []

    # Find citations such as:
    # [Source 1: sample.pdf, Page 2]
    citation_pattern = re.compile(
        r"\[Source\s+(\d+):\s*([^,\]]+)"
        r"(?:,\s*Page\s+(\d+))?\]"
    )

    citations = citation_pattern.findall(answer)

    for source_number, file_name, page_number in citations:

        source_index = int(source_number) - 1

        # Make sure the source number exists
        if source_index < 0:
            continue

        if source_index >= len(documents):
            continue

        document = documents[source_index]

        # Check filename
        if document["file_name"].lower() != file_name.strip().lower():
            continue

        # Check page number for PDF documents
        if page_number:

            document_page = document.get(
                "page_number"
            )

            if document_page is None:
                continue

            if document_page != int(page_number):
                continue

        source_text = document["text"].lower()

        # Remove the citation itself from the answer
        answer_without_citation = re.sub(
            r"\[Source\s+\d+:[^\]]+\]",
            "",
            answer
        ).lower()

        source_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                source_text
            )
        )

        answer_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                answer_without_citation
            )
        )

        common_words = (
            source_words.intersection(
                answer_words
            )
        )

        # Basic evidence-support check
        if len(common_words) >= 3:

            verified_source = {
                "file_name": document["file_name"]
            }

            if "page_number" in document:

                verified_source["page_number"] = (
                    document["page_number"]
                )

            verified_sources.append(
                verified_source
            )

    return verified_sources