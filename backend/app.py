from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.ingestion.pdf_ingest import ingest_pdf
from backend.retrieval.pdf_hybrid_search import PDFHybridSearch
from backend.generation.llm import generate_answer


# -------------------------
# Create FastAPI Application
# -------------------------

app = FastAPI(
    title="EvidenceAI API",
    description="Hybrid-search RAG API with citation verification",
    version="1.1.0"
)


# -------------------------
# Enable CORS
# -------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# PDF Knowledge Base
# -------------------------

PDF_FOLDER = Path("data/pdf_documents")


def load_knowledge_base():

    PDF_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    pdf_files = list(
        PDF_FOLDER.glob("*.pdf")
    )

    if not pdf_files:
        raise RuntimeError(
            "No PDF documents found in "
            "data/pdf_documents/"
        )

    all_chunks = []

    for pdf_file in pdf_files:

        print(
            f"Loading PDF: {pdf_file.name}"
        )

        chunks = ingest_pdf(
            str(pdf_file)
        )

        all_chunks.extend(chunks)

    if not all_chunks:
        raise RuntimeError(
            "No text could be extracted "
            "from the PDF documents."
        )

    print(
        f"Total PDFs loaded: {len(pdf_files)}"
    )

    print(
        f"Total chunks created: {len(all_chunks)}"
    )

    return all_chunks


# Load all PDFs when the API starts

chunks = load_knowledge_base()

search_engine = PDFHybridSearch(
    chunks
)


# -------------------------
# Request Model
# -------------------------

class QueryRequest(BaseModel):
    question: str


# -------------------------
# Root Endpoint
# -------------------------

@app.get("/")
def root():

    return {
        "message": "EvidenceAI API is running",
        "documents_loaded": len(
            set(
                chunk["file_name"]
                for chunk in chunks
            )
        ),
        "total_chunks": len(chunks)
    }


# -------------------------
# Ask EvidenceAI
# -------------------------

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