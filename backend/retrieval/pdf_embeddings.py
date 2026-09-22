from backend.ingestion.pdf_ingest import ingest_pdf
from backend.retrieval.embeddings import generate_embeddings


if __name__ == "__main__":
    pdf_path = "data/pdf_documents/sample.pdf"

    chunks = ingest_pdf(pdf_path)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = generate_embeddings(texts)

    print("Number of chunks:", len(chunks))
    print("Embedding shape:", embeddings.shape)

    print("\nFirst chunk metadata:")
    print("File:", chunks[0]["file_name"])
    print("Page:", chunks[0]["page_number"])