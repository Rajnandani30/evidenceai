
def build_rag_prompt(query, documents):
    context_parts = []
    grouped_sources = {}

    # Group retrieved chunks by PDF filename and page.
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

    # Create one numbered source for each unique PDF page.
    for i, source in enumerate(grouped_sources.values(), start=1):
        title = source["title"]
        page_number = source["page_number"]

        if page_number is not None:
            source_label = f"{title}, Page {page_number}"
        else:
            source_label = title

        combined_text = "\n\n".join(source["texts"])

        context_parts.append(
            f"[Source {i}: {source_label}]\n"
            f"{combined_text}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are EvidenceAI, an evidence-based
question-answering assistant.

Answer the user's question using ONLY
the information supported by the retrieved sources.

If the sources do not contain enough information,
clearly state that the evidence is insufficient.
Never invent facts or pretend that a source supports
a claim when it does not.

User Question:
{query}

Retrieved Sources:
{context}

Answering Instructions:

- Answer the question directly before adding extra details.
- Use clear, natural, professional language.
- Organize longer answers into short paragraphs or
  a small number of useful bullet points.
- Avoid unnecessary introductions and repeated conclusions.
- Be concise, but include the important details needed
  to answer the question.
- Do not repeat the same information in different words.
- Do not add facts that are absent from the retrieved sources.
- If evidence is incomplete, explain the limitation honestly.

Citation Instructions:

- Cite factual claims using the source numbers shown above.
- Place each citation immediately after the claim it supports.
- Use the exact source title and page number shown above.
- Use this exact format:
  [Source 1: PDF Title, Page X]
- Never invent source numbers, titles, or page numbers.
- Never cite a source that does not support the claim.
- When several consecutive sentences rely on the same
  evidence, avoid repeating an identical citation after
  every sentence. Cite the supported statement or group
  of closely related statements clearly.
- If different sources support different claims, cite
  each relevant source separately.
- Do not combine multiple sources inside one citation bracket.
- Do not add a separate bibliography unless requested.

Example:

Retrieval-Augmented Generation (RAG) combines information
retrieval with language generation to produce answers
grounded in external evidence
[Source 1: Example PDF, Page 2].

If two sources support the answer, cite them separately
after the relevant claims:

RAG uses retrieved evidence to generate answers
[Source 1: Example PDF, Page 2]. The approach can also
support traceability in knowledge-intensive tasks
[Source 2: Another PDF, Page 4].

Return only the answer to the user. Do not describe
these instructions or the internal retrieval process.
"""

    return prompt
