import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [activePage, setActivePage] = useState("ask");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");

  // Delete PDF states
  const [deletingFile, setDeletingFile] = useState(null);
  const [deleteMessage, setDeleteMessage] = useState("");
  const [deleteError, setDeleteError] = useState(false);

  const API_URL = "http://127.0.0.1:8000";

  const navigation = [
    { id: "ask", label: "Ask EvidenceAI", icon: "✦" },
    { id: "library", label: "Document Library", icon: "▤" },
    { id: "upload", label: "Upload Documents", icon: "↑" },
  ];

  // -------------------------
  // Format AI Answer
  // -------------------------

  const formatAnswer = (text) => {
    if (!text) return null;

    const cleanedText = text.replace(/\*\*/g, "").trim();

    const lines = cleanedText
      .split(/\n|(?=\s*[-*]\s)/)
      .map((line) => line.replace(/^\s*[-*]\s*/, "").trim())
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

  // -------------------------
  // Fetch Documents
  // -------------------------

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
    } catch {
      setDocumentsError(
        "Unable to load documents. Make sure the backend is running."
      );
    } finally {
      setDocumentsLoading(false);
    }
  };

  // Load documents when application starts

  useEffect(() => {
    fetchDocuments();
  }, []);

  // -------------------------
  // Ask EvidenceAI
  // -------------------------

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
    } catch {
      setAnswer(
        "Unable to connect to EvidenceAI backend. Make sure the FastAPI server is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // -------------------------
  // Upload PDF
  // -------------------------

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
        throw new Error(data.detail || "PDF upload failed.");
      }

      setUploadMessage(
        `${data.message} ${data.file_name} — ${data.pages_processed} pages processed, ${data.chunks_created} chunks created.`
      );

      setSelectedFile(null);

      const fileInput = document.getElementById("pdf-upload");

      if (fileInput) {
        fileInput.value = "";
      }

      await fetchDocuments();
    } catch (error) {
      setUploadMessage(error.message || "Unable to upload PDF.");
      setUploadError(true);
    } finally {
      setUploading(false);
    }
  };

  // -------------------------
  // Delete PDF
  // -------------------------

  const deletePDF = async (fileName) => {
    // Ask confirmation before deleting

    const confirmed = window.confirm(
      `Are you sure you want to permanently delete "${fileName}"?\n\nThis will remove the PDF and its indexed content from EvidenceAI.`
    );

    // Stop if user clicks Cancel

    if (!confirmed) {
      return;
    }

    setDeletingFile(fileName);
    setDeleteMessage("");
    setDeleteError(false);

    try {
      const response = await fetch(
        `${API_URL}/documents/${encodeURIComponent(fileName)}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to delete PDF.");
      }

      // Show success message

      setDeleteMessage(
        `"${fileName}" was deleted successfully.`
      );

      // Refresh document library and dashboard statistics

      await fetchDocuments();
    } catch (error) {
      setDeleteMessage(
        error.message || "Unable to delete PDF."
      );

      setDeleteError(true);
    } finally {
      setDeletingFile(null);
    }
  };

  // -------------------------
  // Dashboard Statistics
  // -------------------------

  const totalPages = documents.reduce(
    (total, doc) => total + doc.pages,
    0
  );

  const totalChunks = documents.reduce(
    (total, doc) => total + doc.chunks,
    0
  );

  const pageTitles = {
    ask: "Ask EvidenceAI",
    library: "Document Library",
    upload: "Upload Documents",
  };

  // -------------------------
  // Main Application UI
  // -------------------------

  return (
    <div className="app dashboard-layout">

      {/* Sidebar */}

      <aside className="sidebar">

        <div className="sidebar-brand">
          <div className="brand-icon">E</div>

          <div>
            <h2>EvidenceAI</h2>
            <span>Research workspace</span>
          </div>
        </div>

        <div className="sidebar-section-label">
          WORKSPACE
        </div>

        <nav className="sidebar-nav">
          {navigation.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                activePage === item.id ? "active" : ""
              }`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span className="status-dot"></span>

            <div>
              <strong>EvidenceAI</strong>
              <small>Document-based AI</small>
            </div>
          </div>
        </div>

      </aside>

      {/* Main workspace */}

      <div className="dashboard-main">

        {/* Top bar */}

        <header className="dashboard-topbar">
          <div>
            <span className="topbar-label">
              EVIDENCEAI / WORKSPACE
            </span>

            <h1>{pageTitles[activePage]}</h1>
          </div>

          <div className="topbar-stats">
            <span className="topbar-dot"></span>
            {documents.length} Documents
          </div>
        </header>

        <main className="dashboard-content">

          {/* =========================
              ASK EVIDENCEAI PAGE
          ========================= */}

          {activePage === "ask" && (
            <section className="workspace-page">

              <div className="welcome-banner">
                <div>
                  <span className="banner-label">
                    AI RESEARCH ASSISTANT
                  </span>

                  <h2>
                    Ask questions.
                    <br />
                    <span>Get evidence.</span>
                  </h2>

                  <p>
                    Search your documents using hybrid retrieval,
                    reranking, and citation verification.
                  </p>
                </div>

                <div className="banner-art">✦</div>
              </div>

              {/* Overview Statistics */}

              <div className="overview-stats">

                <div className="overview-stat">
                  <span className="overview-stat-icon">▤</span>

                  <div>
                    <strong>{documents.length}</strong>
                    <span>Documents</span>
                  </div>
                </div>

                <div className="overview-stat">
                  <span className="overview-stat-icon">▧</span>

                  <div>
                    <strong>{totalPages}</strong>
                    <span>Total Pages</span>
                  </div>
                </div>

                <div className="overview-stat">
                  <span className="overview-stat-icon">⌘</span>

                  <div>
                    <strong>{totalChunks}</strong>
                    <span>Indexed Chunks</span>
                  </div>
                </div>

              </div>

              {/* Question Card */}

              <section className="question-card">

                <div className="section-heading">
                  <div>
                    <h2>Ask your question</h2>

                    <p>
                      Ask anything about your uploaded documents.
                    </p>
                  </div>

                  <span className="ai-badge">
                    AI POWERED
                  </span>
                </div>

                <textarea
                  id="question-input"
                  value={question}
                  onChange={(event) =>
                    setQuestion(event.target.value)
                  }
                  placeholder="Example: What is Retrieval Augmented Generation (RAG)?"
                />

                <div className="question-actions">
                  <span className="input-hint">
                    Answers are grounded in your documents.
                  </span>

                  <button
                    onClick={askQuestion}
                    disabled={loading || !question.trim()}
                  >
                    {loading
                      ? "Searching Evidence..."
                      : "✦ Ask EvidenceAI"}
                  </button>
                </div>

              </section>

              {/* Loading Message */}

              {loading && (
                <div className="answer-card">
                  <p className="documents-status">
                    Searching documents and generating your answer...
                  </p>
                </div>
              )}

              {/* AI Answer */}

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
                    <div className="source" key={index}>
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

            </section>
          )}

          {/* =========================
              DOCUMENT LIBRARY PAGE
          ========================= */}

          {activePage === "library" && (
            <section className="workspace-page">

              <div className="page-intro">
                <div>
                  <h2>Your Documents</h2>

                  <p>
                    Browse and manage the documents indexed
                    in your EvidenceAI knowledge base.
                  </p>
                </div>

                <button
                  className="refresh-button"
                  onClick={fetchDocuments}
                  disabled={documentsLoading}
                >
                  {documentsLoading
                    ? "Refreshing..."
                    : "↻ Refresh"}
                </button>
              </div>

              {/* Library Statistics */}

              <div className="overview-stats">

                <div className="overview-stat">
                  <span className="overview-stat-icon">▤</span>

                  <div>
                    <strong>{documents.length}</strong>
                    <span>Documents</span>
                  </div>
                </div>

                <div className="overview-stat">
                  <span className="overview-stat-icon">▧</span>

                  <div>
                    <strong>{totalPages}</strong>
                    <span>Total Pages</span>
                  </div>
                </div>

                <div className="overview-stat">
                  <span className="overview-stat-icon">⌘</span>

                  <div>
                    <strong>{totalChunks}</strong>
                    <span>Total Chunks</span>
                  </div>
                </div>

              </div>

              {/* Documents Card */}

              <section className="documents-card">

                <div className="documents-header">
                  <div>
                    <h2>Indexed Documents</h2>

                    <p>
                      All PDFs currently available for AI search.
                    </p>
                  </div>

                  <button
                    onClick={() => setActivePage("upload")}
                  >
                    + Add PDF
                  </button>
                </div>

                {/* Delete Success/Error Message */}

                {deleteMessage && (
                  <p
                    className={`upload-message ${
                      deleteError ? "error" : "success"
                    }`}
                  >
                    {deleteMessage}
                  </p>
                )}

                {/* Loading State */}

                {documentsLoading && (
                  <p className="documents-status">
                    Loading your documents...
                  </p>
                )}

                {/* Error State */}

                {documentsError && (
                  <p className="upload-message error">
                    {documentsError}
                  </p>
                )}

                {/* Empty Library */}

                {!documentsLoading &&
                  !documentsError &&
                  documents.length === 0 && (
                    <div className="empty-library">
                      <span>▤</span>

                      <h3>No documents yet</h3>

                      <p>
                        Upload a PDF to start building your
                        knowledge base.
                      </p>

                      <button
                        onClick={() => setActivePage("upload")}
                      >
                        Upload your first PDF
                      </button>
                    </div>
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
                            <h3>{document.file_name}</h3>

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

                          {/* DELETE BUTTON */}

                          <button
                            type="button"
                            className="delete-button"
                            onClick={() =>
                              deletePDF(document.file_name)
                            }
                            disabled={deletingFile !== null}
                            style={{
                              backgroundColor: "#dc3545",
                              color: "#ffffff",
                              border: "none",
                              borderRadius: "8px",
                              padding: "10px 18px",
                              cursor:
                                deletingFile !== null
                                  ? "not-allowed"
                                  : "pointer",
                              opacity:
                                deletingFile !== null
                                  ? 0.6
                                  : 1,
                              fontWeight: "600",
                              marginLeft: "12px",
                            }}
                          >
                            {deletingFile === document.file_name
                              ? "Deleting..."
                              : "Delete"}
                          </button>

                        </div>
                      ))}

                    </div>
                  )}

              </section>

            </section>
          )}

          {/* =========================
              UPLOAD DOCUMENTS PAGE
          ========================= */}

          {activePage === "upload" && (
            <section className="workspace-page">

              <div className="page-intro">
                <div>
                  <h2>Add documents</h2>

                  <p>
                    Upload PDFs to expand your EvidenceAI
                    knowledge base.
                  </p>
                </div>
              </div>

              {/* Upload Card */}

              <section className="upload-card">

                <div className="upload-heading-icon">
                  ↑
                </div>

                <h2>Upload your PDF</h2>

                <p>
                  Select a PDF document. EvidenceAI will process
                  its pages, create chunks, and index the content
                  for question answering.
                </p>

                <div className="upload-drop-area">

                  <span className="upload-file-icon">
                    PDF
                  </span>

                  <h3>
                    {selectedFile
                      ? selectedFile.name
                      : "Choose a PDF document"}
                  </h3>

                  <p>
                    PDF files only
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

                </div>

                <button
                  onClick={uploadPDF}
                  disabled={uploading || !selectedFile}
                >
                  {uploading
                    ? "Uploading and Indexing..."
                    : "↑ Upload and Index PDF"}
                </button>

                {/* Upload Message */}

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

                {!uploadError &&
                  uploadMessage &&
                  !uploading && (
                    <button
                      className="refresh-button"
                      onClick={() => setActivePage("library")}
                    >
                      View Document Library →
                    </button>
                  )}

              </section>

              {/* Upload Information */}

              <div className="upload-info-card">
                <span>✦</span>

                <div>
                  <strong>
                    What happens after upload?
                  </strong>

                  <p>
                    EvidenceAI extracts PDF text, creates
                    searchable chunks, and updates its retrieval
                    index so you can ask questions about the
                    document.
                  </p>
                </div>
              </div>

            </section>
          )}

        </main>

        {/* Footer */}

        <footer className="dashboard-footer">
          EvidenceAI · Hybrid Search · Retrieval-Augmented Generation
        </footer>

      </div>
    </div>
  );
}

export default App;