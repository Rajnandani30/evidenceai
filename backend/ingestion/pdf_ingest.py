from backend.ingestion.pdf_loader import load_pdf
from backend.ingestion.chunker import chunk_pdf_pages


def ingest_pdf(file_path, chunk_size=100):
    pages = load_pdf(file_path)

    chunks = chunk_pdf_pages(
        pages,
        chunk_size=chunk_size
    )

    return chunks


if __name__ == "__main__":
    pdf_path = "data/pdf_documents/sample.pdf"

    chunks = ingest_pdf(pdf_path)

    print("PDF ingestion completed.")
    print("Total chunks:", len(chunks))

    print("\nFirst chunk:")
    print(chunks[0])