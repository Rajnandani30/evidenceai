
import { useState } from "react";
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

  // Format answer into readable bullet points
  const formatAnswer = (text) => {
    if (!text) return null;

    const cleanedText = text
      .replace(/\\\*/g, "*")
      .trim();

    const lines = cleanedText
      .split(/\n|(?=\s*\*\s)/)
      .map((line) => line.replace(/^\s*\*\s*/, "").trim())
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

  // Ask EvidenceAI
  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
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

      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

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
      <header className="header">
        <div>
          <h1>EvidenceAI</h1>
          <p>Evidence-based AI Question Answering</p>
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <h2>Ask questions. Get evidence.</h2>
          <p>
            EvidenceAI uses hybrid search, reranking and citation verification
            to generate answers grounded in your documents.
          </p>
        </section>

        {/* PDF Upload Section */}
        <section className="upload-card">
          <h2>Upload Your Documents</h2>

          <p>
            Upload a PDF to add it to the EvidenceAI knowledge base.
          </p>

          <input
            id="pdf-upload"
            type="file"
            accept=".pdf,application/pdf"
            onChange={(event) => {
              setSelectedFile(event.target.files[0] || null);
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
            {uploading ? "Uploading and Indexing..." : "Upload PDF"}
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

        {/* Question Section */}
        <section className="question-card">
          <label htmlFor="question-input">
            Ask your question
          </label>

          <textarea
            id="question-input"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Example: What is Retrieval Augmented Generation (RAG)?"
          />

          <button onClick={askQuestion} disabled={loading}>
            {loading ? "Searching Evidence..." : "Ask EvidenceAI"}
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
              <div className="source" key={index}>
                <strong>
                  {source.title || source.file_name || "Document"}
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