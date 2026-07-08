import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "https://support-agent-crew.onrender.com";

function App() {
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subject.trim() || !message.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await axios.post(`${API_URL}/tickets/process`, {
        subject,
        message,
      });

      const newTicket = {
        id: Date.now(),
        subject,
        message,
        ...res.data,
      };

      setTickets([newTicket, ...tickets]);
      setSubject("");
      setMessage("");
    } catch (err) {
      setError("Couldn't process this ticket. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const isEscalated = (review) => review?.toLowerCase().includes("escalate: yes");

  return (
    <div className="app">
      <header className="header">
        <h1>Support Ticket Triage</h1>
        <p className="subtitle">Multi-agent classification, retrieval &amp; response</p>
      </header>

      <div className="layout">
        <section className="panel form-panel">
          <h2>New ticket</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Subject
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. Refund request"
                disabled={loading}
              />
            </label>
            <label>
              Message
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Describe the customer's issue..."
                rows={6}
                disabled={loading}
              />
            </label>
            <button type="submit" disabled={loading}>
              {loading ? "Processing through agents..." : "Submit ticket"}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
        </section>

        <section className="panel results-panel">
          <h2>Processed tickets ({tickets.length})</h2>
          {tickets.length === 0 && (
            <p className="empty">No tickets processed yet. Submit one to see the agent pipeline in action.</p>
          )}
          <div className="ticket-list">
            {tickets.map((t) => (
              <div key={t.id} className={`ticket-card ${isEscalated(t.escalation_review) ? "escalated" : ""}`}>
                <div className="ticket-card-header">
                  <h3>{t.subject}</h3>
                  {isEscalated(t.escalation_review) ? (
                    <span className="badge badge-escalate">Escalated</span>
                  ) : (
                    <span className="badge badge-ok">Auto-resolved</span>
                  )}
                </div>
                <p className="original-message">{t.message}</p>

                <div className="ticket-section">
                  <span className="ticket-label">Classification</span>
                  <p>{t.classification}</p>
                </div>

                <div className="ticket-section">
                  <span className="ticket-label">Draft response</span>
                  <p className="draft-response">{t.draft_response}</p>
                </div>

                <div className="ticket-section">
                  <span className="ticket-label">Escalation review</span>
                  <p>{t.escalation_review}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
