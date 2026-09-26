import re
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
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
    version="1.3.0"
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

# Protect the knowledge base from simultaneous updates
knowledge_base_lock = Lock()


def load_knowledge_base():

    PDF_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    pdf_files = list(
        PDF_FOLDER.glob("*.pdf")
    )

    all_chunks = []

    for pdf_file in pdf_files:

        print(f"Loading PDF: {pdf_file.name}")

        chunks = ingest_pdf(
            str(pdf_file)
        )

        all_chunks.extend(chunks)

    print(f"Total PDFs loaded: {len(pdf_files)}")
    print(f"Total chunks created: {len(all_chunks)}")

    return all_chunks


# Load existing PDFs when the API starts

chunks = load_knowledge_base()

search_engine = PDFHybridSearch(chunks)


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

    with knowledge_base_lock:

        documents_loaded = len(
            set(
                chunk["file_name"]
                for chunk in chunks
            )
        )

        total_chunks = len(chunks)

    return {
        "message": "EvidenceAI API is running",
        "documents_loaded": documents_loaded,
        "total_chunks": total_chunks
    }


# -------------------------
# Document Library
# -------------------------

@app.get("/documents")
def get_documents():

    with knowledge_base_lock:

        documents = {}

        for chunk in chunks:

            file_name = chunk["file_name"]

            if file_name not in documents:

                documents[file_name] = {
                    "file_name": file_name,
                    "pages": set(),
                    "chunks": 0
                }

            documents[file_name]["pages"].add(
                chunk["page_number"]
            )

            documents[file_name]["chunks"] += 1

        document_list = []

        for document in documents.values():

            document_list.append({
                "file_name": document["file_name"],
                "pages": len(document["pages"]),
                "chunks": document["chunks"]
            })

    return {
        "total_documents": len(document_list),
        "documents": document_list
    }


# -------------------------
# Upload PDF
# -------------------------

@app.post("/upload")
def upload_pdf(
    file: UploadFile = File(...)
):

    global chunks, search_engine

    # Check the uploaded file extension

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Generate a unique filename to avoid overwriting files

    original_name = Path(file.filename).name

    safe_name = (
        f"{Path(original_name).stem}_{uuid4().hex[:8]}.pdf"
    )

    file_path = PDF_FOLDER / safe_name

    try:

        # Read uploaded file

        contents = file.file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        # Save uploaded PDF

        PDF_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(file_path, "wb") as pdf_file:
            pdf_file.write(contents)

        # Extract text and create chunks

        new_chunks = ingest_pdf(
            str(file_path)
        )

        if not new_chunks:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF."
            )

        # Update the knowledge base safely

        with knowledge_base_lock:

            updated_chunks = chunks + new_chunks

            updated_search_engine = PDFHybridSearch(
                updated_chunks
            )

            chunks = updated_chunks
            search_engine = updated_search_engine

            documents_loaded = len(
                set(
                    chunk["file_name"]
                    for chunk in chunks
                )
            )

        return {
            "message": "PDF uploaded and indexed successfully.",
            "file_name": safe_name,
            "pages_processed": len(
                set(
                    chunk["page_number"]
                    for chunk in new_chunks
                )
            ),
            "chunks_created": len(new_chunks),
            "documents_loaded": documents_loaded
        }

    except HTTPException:
        # Remove invalid uploaded files

        if file_path.exists():
            file_path.unlink()

        raise

    except Exception as error:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"PDF upload failed: {str(error)}"
        )

    finally:
        file.file.close()



# -------------------------
# Ask EvidenceAI
# -------------------------

@app.post("/ask")
def ask_question(request: QueryRequest):

    global chunks, search_engine

    query = request.question.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Detect a PDF filename in the question
    filename_match = re.search(
        r'(?:named|in|from|about)\s+["\']?([A-Za-z0-9_.-]+\.pdf)',
        query,
        re.IGNORECASE
    )

    # Also support questions that contain only a filename
    if not filename_match:
        filename_match = re.search(
            r'\b([A-Za-z0-9_.-]+\.pdf)\b',
            query,
            re.IGNORECASE
        )

    requested_filename = (
        filename_match.group(1)
        if filename_match
        else None
    )

    # Get the current knowledge base safely
    with knowledge_base_lock:
        current_chunks = list(chunks)
        current_search_engine = search_engine

    # -------------------------
    # Search a specific PDF
    # -------------------------

    if requested_filename:

        matching_chunks = [
            chunk
            for chunk in current_chunks
            if chunk["file_name"].lower()
            == requested_filename.lower()
        ]

        if not matching_chunks:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"PDF '{requested_filename}' "
                    "was not found in the library."
                )
            )

        print(
            f"Searching only in PDF: "
            f"{requested_filename}"
        )

        # Remove the filename from the search query
        search_query = re.sub(
            re.escape(requested_filename),
            "",
            query,
            flags=re.IGNORECASE
        ).strip()

        if not search_query:
            search_query = query

        # Build a search engine for the selected PDF only
        document_search_engine = PDFHybridSearch(
            matching_chunks
        )

        results = document_search_engine.search(
            search_query,
            top_k=5
        )

    # -------------------------
    # Search all PDFs normally
    # -------------------------

    else:

        results = current_search_engine.search(
            query,
            top_k=5
        )

    # -------------------------
    # Retrieval Debug
    # -------------------------

    print("\n========== RETRIEVAL DEBUG ==========")
    print("Question:", query)
    print("Requested PDF:", requested_filename)
    print("Number of retrieved results:", len(results))

    for i, result in enumerate(results, start=1):

        print(f"\n--- Result {i} ---")
        print("File:", result.get("file_name"))
        print("Page:", result.get("page_number"))
        print("Score:", result.get("hybrid_score"))
        print("Text:", result.get("text", "")[:500])

    print("\n========== END RETRIEVAL DEBUG ==========\n")

    # -------------------------
    # Generate Answer
    # -------------------------

    answer, verified_sources = generate_answer(
        query,
        results
    )

    return {
        "question": query,
        "answer": answer,
        "verified_sources": verified_sources
    }