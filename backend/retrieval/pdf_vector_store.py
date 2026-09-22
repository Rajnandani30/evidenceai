from backend.ingestion.pdf_ingest import ingest_pdf
from backend.retrieval.embeddings import generate_embeddings
from backend.retrieval.vector_store import VectorStore


if __name__ == "__main__":
    pdf_path = "data/pdf_documents/sample.pdf"

    chunks = ingest_pdf(pdf_path)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = generate_embeddings(texts)

    store = VectorStore(
        dimension=embeddings.shape[1]
    )

    store.add_embeddings(embeddings)

    print("PDF chunks:", len(chunks))
    print("FAISS vectors:", store.index.ntotal)
    print("Vector dimension:", embeddings.shape[1])