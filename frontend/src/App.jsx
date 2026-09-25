
import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  // Format answer text into readable bullet points
  const formatAnswer = (text) => {
    if (!text) return null;

    // Remove literal escaped asterisks and clean up whitespace
    const cleanedText = text
      .replace(/\\\*/g, "*")
      .trim();

    // Split the answer into separate lines
    const lines = cleanedText
      .split(/\n|(?=\s*\*\s)/)
      .map((line) => line.replace(/^\s*\*\s*/, "").trim())
      .filter(Boolean);

    // Display as bullet points when the answer contains multiple items
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
        throw new Error("Failed to get an answer from the backend.");
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

        <section className="question-card">
          <label htmlFor="question-input">Ask your question</label>

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

        {answer && (
          <section className="answer-card">
            <h2>Answer</h2>

            <div className="answer">
              {formatAnswer(answer)}
            </div>
          </section>
        )}

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