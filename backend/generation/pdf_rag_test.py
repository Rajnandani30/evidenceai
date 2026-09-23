from backend.ingestion.pdf_ingest import ingest_pdf
from backend.retrieval.pdf_hybrid_search import PDFHybridSearch
from backend.generation.llm import generate_answer


if __name__ == "__main__":

    pdf_path = "data/pdf_documents/sample.pdf"

    # Load and chunk PDF
    chunks = ingest_pdf(pdf_path)

    # Create PDF hybrid search
    search_engine = PDFHybridSearch(chunks)

    # User question
    query = "What is Retrieval Augmented Generation (RAG)?"

    # Retrieve relevant evidence
    results = search_engine.search(
        query,
        top_k=5
    )

    # Generate answer using Gemini
    answer, verified_sources = generate_answer(
        query,
        results
    )

    print("\n==============================")
    print("EvidenceAI PDF Answer")
    print("==============================")

    print("\nQuestion:")
    print(query)

    print("\nAnswer:")
    print(answer)

    print("\nVerified Sources:")

    for source in verified_sources:
        print("-", source)