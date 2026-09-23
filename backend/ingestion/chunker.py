def chunk_text(text, chunk_size=100):
    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        if chunk.strip():
            chunks.append(chunk)

    return chunks


def chunk_documents(documents, chunk_size=100):

    chunks = []

    for document in documents:

        text_chunks = chunk_text(
            document["text"],
            chunk_size
        )

        for chunk in text_chunks:

            chunks.append(
                {
                    "file_name": document["file_name"],
                    "text": chunk,
                }
            )

    return chunks


def chunk_pdf_pages(pages, chunk_size=100):

    chunks = []

    for page in pages:

        words = page["text"].split()

        for i in range(
            0,
            len(words),
            chunk_size
        ):

            chunk_text_value = " ".join(
                words[i:i + chunk_size]
            )

            if chunk_text_value.strip():

                chunks.append(
                    {
                        "file_name": page["file_name"],
                        "title": page.get(
                            "title",
                            page["file_name"]
                        ),
                        "author": page.get(
                            "author",
                            "Unknown"
                        ),
                        "page_number": page["page_number"],
                        "source": page.get(
                            "source",
                            page["file_name"]
                        ),
                        "text": chunk_text_value,
                    }
                )

    return chunks