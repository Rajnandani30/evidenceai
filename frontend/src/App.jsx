
import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState(false);

  // Document Library states
  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");

  const API_URL = "http://127.0.0.1:8000";

  // Format answer into readable bullet points
  const formatAnswer = (text) => {
    if (!text) return null;

    const cleanedText = text
      .replace(/\*\*/g, "")
      .trim();

    const lines = cleanedText
      .split(/\n|(?=\s*[-*]\s)/)
      .map((line) =>
        line.replace(/^\s*[-*]\s*/, "").trim()
      )
      .filter(Boolean);

    if (lines.length > 1) {
      return (
        <ul className="answer-list">
          {lines.map((line, index) => (
            <li key={index}>{line}</li>
          ))}
        </ul>
      );
    }

    return <p>{cleanedText}</p>;
  };

  // Fetch Document Library from backend
  const fetchDocuments = async () => {
    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      const response = await fetch(`${API_URL}/documents`);

      if (!response.ok) {
        throw new Error("Failed to load documents.");
      }

      const data = await response.json();

      setDocuments(data.documents || []);
    } catch (error) {
      setDocumentsError(
        "Unable to load documents. Make sure the backend is running."
      );
    } finally {
      setDocumentsLoading(false);
    }
  };

  // Load documents when the dashboard opens
  useEffect(() => {
    fetchDocuments();
  }, []);

  // Ask EvidenceAI
  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get an answer.");
      }

      const data = await response.json();

      setAnswer(data.answer || "No answer was generated.");
      setSources(data.verified_sources || []);
    } catch (error) {
      setAnswer(
        "Unable to connect to EvidenceAI backend. Make sure the FastAPI server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // Upload PDF to backend
  const uploadPDF = async () => {
    if (!selectedFile) {
      setUploadMessage("Please select a PDF file first.");
      setUploadError(true);
      return;
    }

    setUploading(true);
    setUploadMessage("");
    setUploadError(false);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "PDF upload failed."
        );
      }

      setUploadMessage(
        `${data.message} ${data.file_name} — ${data.pages_processed} pages processed, ${data.chunks_created} chunks created.`
      );

      setSelectedFile(null);

      // Clear the file input after successful upload
      const fileInput = document.getElementById("pdf-upload");

      if (fileInput) {
        fileInput.value = "";
      }

      // Refresh Document Library after successful upload
      await fetchDocuments();

    } catch (error) {
      setUploadMessage(
        error.message || "Unable to upload PDF."
      );

      setUploadError(true);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div>
          <h1>EvidenceAI</h1>
          <p>Evidence-based AI Question Answering</p>
        </div>
      </header>

      <main className="container">

        {/* Hero Section */}
        <section className="hero">
          <h2>Ask questions. Get evidence.</h2>

          <p>
            EvidenceAI uses hybrid search, reranking and
            citation verification to generate answers
            grounded in your documents.
          </p>
        </section>

        {/* PDF Upload Section */}
        <section className="upload-card">
          <h2>Upload Your Documents</h2>

          <p>
            Upload a PDF to add it to the EvidenceAI
            knowledge base.
          </p>

          <input
            id="pdf-upload"
            type="file"
            accept=".pdf,application/pdf"
            onChange={(event) => {
              setSelectedFile(
                event.target.files[0] || null
              );

              setUploadMessage("");
              setUploadError(false);
            }}
          />

          {selectedFile && (
            <p className="selected-file">
              Selected: {selectedFile.name}
            </p>
          )}

          <button
            onClick={uploadPDF}
            disabled={uploading || !selectedFile}
          >
            {uploading
              ? "Uploading and Indexing..."
              : "Upload PDF"}
          </button>

          {uploadMessage && (
            <p
              className={
                uploadError
                  ? "upload-message error"
                  : "upload-message success"
              }
            >
              {uploadMessage}
            </p>
          )}
        </section>

        {/* Document Library Section */}
        <section className="documents-card">

          <div className="documents-header">
            <div>
              <h2>Document Library</h2>

              <p>
                Browse the documents indexed in EvidenceAI.
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={fetchDocuments}
              disabled={documentsLoading}
            >
              {documentsLoading
                ? "Refreshing..."
                : "Refresh"}
            </button>
          </div>

          {/* Document Statistics */}
          <div className="document-stats">

            <div className="stat-box">
              <span className="stat-number">
                {documents.length}
              </span>

              <span className="stat-label">
                Documents
              </span>
            </div>

            <div className="stat-box">
              <span className="stat-number">
                {documents.reduce(
                  (total, doc) => total + doc.pages,
                  0
                )}
              </span>

              <span className="stat-label">
                Total Pages
              </span>
            </div>

            <div className="stat-box">
              <span className="stat-number">
                {documents.reduce(
                  (total, doc) => total + doc.chunks,
                  0
                )}
              </span>

              <span className="stat-label">
                Total Chunks
              </span>
            </div>

          </div>

          {/* Loading Message */}
          {documentsLoading && (
            <p className="documents-status">
              Loading your documents...
            </p>
          )}

          {/* Error Message */}
          {documentsError && (
            <p className="upload-message error">
              {documentsError}
            </p>
          )}

          {/* Empty Library */}
          {!documentsLoading &&
            !documentsError &&
            documents.length === 0 && (
              <p className="documents-status">
                No documents found. Upload a PDF to get started.
              </p>
            )}

          {/* Document List */}
          {!documentsLoading &&
            documents.length > 0 && (
              <div className="document-list">

                {documents.map((document, index) => (
                  <div
                    className="document-item"
                    key={document.file_name}
                  >

                    <div className="document-icon">
                      PDF
                    </div>

                    <div className="document-info">
                      <h3>
                        {document.file_name}
                      </h3>

                      <div className="document-meta">
                        <span>
                          {document.pages}{" "}
                          {document.pages === 1
                            ? "Page"
                            : "Pages"}
                        </span>

                        <span className="meta-dot">
                          •
                        </span>

                        <span>
                          {document.chunks}{" "}
                          {document.chunks === 1
                            ? "Chunk"
                            : "Chunks"}
                        </span>
                      </div>
                    </div>

                    <span className="document-number">
                      #{index + 1}
                    </span>

                  </div>
                ))}

              </div>
            )}

        </section>

        {/* Question Section */}
        <section className="question-card">
          <label htmlFor="question-input">
            Ask your question
          </label>

          <textarea
            id="question-input"
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Example: What is Retrieval Augmented Generation (RAG)?"
          />

          <button
            onClick={askQuestion}
            disabled={loading}
          >
            {loading
              ? "Searching Evidence..."
              : "Ask EvidenceAI"}
          </button>
        </section>

        {/* Answer Section */}
        {answer && (
          <section className="answer-card">
            <h2>Answer</h2>

            <div className="answer">
              {formatAnswer(answer)}
            </div>
          </section>
        )}

        {/* Verified Sources */}
        {sources.length > 0 && (
          <section className="sources-card">
            <h2>Verified Sources</h2>

            {sources.map((source, index) => (
              <div
                className="source"
                key={index}
              >
                <strong>
                  {source.title ||
                    source.file_name ||
                    "Document"}
                </strong>

                {source.page_number && (
                  <span className="source-page">
                    Page {source.page_number}
                  </span>
                )}

                <small className="source-file">
                  {source.file_name}
                </small>
              </div>
            ))}
          </section>
        )}

      </main>
    </div>
  );
}

export default App;