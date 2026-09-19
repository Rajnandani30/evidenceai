from loader import load_documents
from chunker import chunk_text


def ingest_documents(data_folder: str):
    documents = load_documents(data_folder)

    all_chunks = []

    for document in documents:
        chunks = chunk_text(document["text"])

        for chunk in chunks:
            all_chunks.append(
                {
                    "file_name": document["file_name"],
                    "text": chunk,
                }
            )

    return all_chunks


if __name__ == "__main__":
    chunks = ingest_documents("data/sample_documents")

    print(f"Created {len(chunks)} chunks from the documents.")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {i} - {chunk['file_name']}:")
        print(chunk["text"])