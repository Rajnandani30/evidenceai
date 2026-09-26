
def build_rag_prompt(query, documents):

    context_parts = []

    # Group chunks by unique PDF filename and page number.
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

    # Build one source entry per unique PDF page.
    for i, source in enumerate(
        grouped_sources.values(),
        start=1
    ):

        title = source["title"]
        page_number = source["page_number"]

        if page_number is not None:

            source_label = f"{title}, Page {page_number}"

        else:

            source_label = title

        # Combine the retrieved chunks from the same page.
        combined_text = "\n\n".join(
            source["texts"]
        )

        context_parts.append(
            f"[Source {i}: {source_label}]\n"
            f"{combined_text}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are EvidenceAI, an evidence-based
question answering assistant.

Answer the user's question using ONLY
the provided sources.

If the sources do not contain enough
information to answer the question,
say that the available evidence is
insufficient.

Do not invent facts.

User Question:
{query}

Retrieved Sources:
{context}

Instructions:

- Give a clear and concise answer.
- Use only information supported by
  the retrieved sources.
- Cite factual claims using the source
  number assigned in Retrieved Sources.
- When available, include the PDF
  title and page number in the citation.
- Use the exact source title and page
  shown in the Retrieved Sources section.
- Do not invent source numbers.
- Do not cite information that is not
  supported by the sources.
- If the evidence is insufficient,
  clearly say so.

Citation format:

[Source 1: PDF Title, Page X]

Example:

RAG combines retrieval with generation
to provide answers grounded in external
information [Source 1: Example PDF, Page 2].
"""

    return prompt