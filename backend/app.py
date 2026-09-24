from fastapi import FastAPI
from pydantic import BaseModel

from backend.ingestion.pdf_ingest import ingest_pdf
from backend.retrieval.pdf_hybrid_search import PDFHybridSearch
from backend.generation.llm import generate_answer


app = FastAPI(
    title="EvidenceAI API",
    description="Hybrid-search RAG API with citation verification",
    version="1.0.0"
)


PDF_PATH = "data/pdf_documents/sample.pdf"


# Load PDF once when the API starts
chunks = ingest_pdf(PDF_PATH)

search_engine = PDFHybridSearch(
    chunks
)


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():

    return {
        "message": "EvidenceAI API is running"
    }


@app.post("/ask")
def ask_question(request: QueryRequest):

    query = request.question

    # Retrieve relevant evidence
    results = search_engine.search(
        query,
        top_k=5
    )

    # Generate answer and verify citations
    answer, verified_sources = generate_answer(
        query,
        results
    )

    return {
        "question": query,
        "answer": answer,
        "verified_sources": verified_sources
    }