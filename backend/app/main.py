from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agents.crew import process_ticket

app = FastAPI(title="Support Agent Crew API")

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev; tighten this before real deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketRequest(BaseModel):
    subject: str
    message: str


@app.get("/")
def health_check():
    return {"status": "ok", "service": "support-agent-crew"}


@app.post("/tickets/process")
def process_ticket_endpoint(ticket: TicketRequest):
    result = process_ticket(subject=ticket.subject, message=ticket.message)
    return result