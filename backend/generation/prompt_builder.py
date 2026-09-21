def build_rag_prompt(query, documents):
    context_parts = []

    for i, document in enumerate(documents, start=1):
        context_parts.append(
            f"[Source {i}: {document['file_name']}]\n"
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
- Use only information supported by the sources.
- Mention the relevant source name when making factual claims.
- If the evidence is insufficient, clearly say so.
"""

    return prompt


if __name__ == "__main__":
    sample_documents = [
        {
            "file_name": "machine_learning.txt",
            "text": "Machine Learning allows computers to learn patterns from data."
        },
        {
            "file_name": "ai_basics.txt",
            "text": "Artificial Intelligence is a field of computer science."
        },
    ]

    prompt = build_rag_prompt(
        "What is Machine Learning?",
        sample_documents
    )

    print(prompt)