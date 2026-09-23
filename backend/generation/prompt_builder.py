def build_rag_prompt(query, documents):
    context_parts = []

    for i, document in enumerate(documents, start=1):

        file_name = document["file_name"]

        page_number = document.get(
            "page_number"
        )

        if page_number is not None:

            source_label = (
                f"{file_name}, Page {page_number}"
            )

        else:

            source_label = file_name

        context_parts.append(
            f"[Source {i}: {source_label}]\n"
            f"{document['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are EvidenceAI, an evidence-based question answering assistant.

Answer the user's question using ONLY the provided sources.

If the sources do not contain enough information to answer the question,
say that the available evidence is insufficient.

Do not invent facts.

User Question:
{query}

Retrieved Sources:
{context}

Instructions:
- Give a clear and concise answer.
- Use only information supported by the retrieved sources.
- Cite factual claims using the source number.
- When available, include the PDF page number in the citation.
- Do not cite information that is not supported by the sources.
- If the evidence is insufficient, clearly say so.

Citation format:
[Source 1: filename, Page X]

Example:
RAG combines retrieval with generation to provide answers grounded in
external information [Source 1: sample.pdf, Page 2].
"""

    return prompt