def chunk_pdf_pages(pages, chunk_size=100):
    chunks = []

    for page in pages:
        words = page["text"].split()

        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(
                words[i:i + chunk_size]
            )

            if chunk_text.strip():
                chunks.append(
                    {
                        "file_name": page["file_name"],
                        "page_number": page["page_number"],
                        "text": chunk_text,
                    }
                )

    return chunks