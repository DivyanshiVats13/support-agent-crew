# Support Agent Crew

A multi-agent AI system that automates customer support ticket triage — classifies incoming tickets, retrieves relevant knowledge base articles, drafts a reply, and flags risky tickets for human review.

**Live demo:** [support-agent-crew.vercel.app](https://support-agent-crew.vercel.app)
**API docs:** [support-agent-crew.onrender.com/docs](https://support-agent-crew.onrender.com/docs)

> The backend runs on a free hosting tier and sleeps when idle. The first request may take 30-60 seconds to wake up.

## What it does

Four AI agents work together on each ticket:

1. **Classifier** — assigns a category and urgency level
2. **Retriever** — searches a knowledge base (ChromaDB) for relevant articles
3. **Responder** — drafts a reply grounded in the retrieved knowledge
4. **Escalation Reviewer** — decides if it's safe to auto-send, or needs a human (refund disputes, angry customers, legal threats always get escalated)

## Tech stack

- **Backend:** FastAPI
- **Multi-agent orchestration:** CrewAI
- **RAG / retrieval:** ChromaDB
- **LLM:** Groq (Llama 3.3 70B)
- **Frontend:** React + Vite
- **Deployment:** Render (backend), Vercel (frontend)

## Running locally

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# add GROQ_API_KEY to a .env file in backend/
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## What's next

- Persist ticket history to a database instead of browser state
- Show a confidence score alongside the escalation decision
- Support multi-message ticket threads