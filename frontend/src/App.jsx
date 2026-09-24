import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

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

      const data = await response.json();

      setAnswer(data.answer);
      setSources(data.verified_sources || []);
    } catch (error) {
      setAnswer(
        "Unable to connect to EvidenceAI backend. Make sure the FastAPI server is running."
      );
    }

    setLoading(false);
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
          <label>Ask your question</label>

          <textarea
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
              {answer}
            </div>
          </section>
        )}

        {sources.length > 0 && (
          <section className="sources-card">
            <h2>Verified Sources</h2>

            {sources.map((source, index) => (
              <div className="source" key={index}>
                <strong>
                  {source.title || source.file_name}
                </strong>

                {source.page_number && (
                  <span>
                    Page {source.page_number}
                  </span>
                )}

                <small>{source.file_name}</small>
              </div>
            ))}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;