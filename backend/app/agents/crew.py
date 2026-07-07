import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from app.agents.tools import KnowledgeBaseSearchTool

load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

kb_tool = KnowledgeBaseSearchTool()

# --- Agents ---

classifier_agent = Agent(
    role="Support Ticket Classifier",
    goal="Accurately classify incoming support tickets by category and urgency",
    backstory=(
        "You are an experienced support triage specialist. You've seen thousands "
        "of tickets and can quickly tell whether something is a billing issue, "
        "technical problem, or account matter, and how urgent it is."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)

retriever_agent = Agent(
    role="Knowledge Base Researcher",
    goal="Find the most relevant knowledge base articles for a given customer issue",
    backstory=(
        "You are a meticulous researcher who always checks the knowledge base "
        "before assuming an answer. You never guess when documentation exists."
    ),
    llm=llm,
    tools=[kb_tool],
    verbose=True,
    allow_delegation=False
)

responder_agent = Agent(
    role="Customer Support Responder",
    goal="Draft a clear, empathetic, and accurate response to the customer using retrieved knowledge",
    backstory=(
        "You are a senior support agent known for warm, precise responses that "
        "resolve issues without unnecessary back-and-forth. You always ground "
        "your answers in the retrieved documentation, never invent policy."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)

escalation_agent = Agent(
    role="Escalation Reviewer",
    goal="Decide whether a drafted response is safe to send or needs human escalation",
    backstory=(
        "You are a quality control lead. You escalate anything involving refund "
        "disputes, legal threats, angry or distressed customers, or cases where "
        "the knowledge base didn't have a confident answer. You are cautious by design."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False
)


def process_ticket(subject: str, message: str):
    classify_task = Task(
        description=(
            f"Classify this support ticket.\n\nSubject: {subject}\nMessage: {message}\n\n"
            "Output the category (billing/technical/account/other) and urgency (low/medium/high), "
            "with a one-line justification."
        ),
        expected_output="Category, urgency level, and a one-line justification.",
        agent=classifier_agent
    )

    retrieve_task = Task(
        description=(
            f"Given this ticket:\nSubject: {subject}\nMessage: {message}\n\n"
            "Search the knowledge base for the most relevant articles to help resolve it."
        ),
        expected_output="The most relevant knowledge base article(s) found, verbatim.",
        agent=retriever_agent,
        context=[classify_task]
    )

    respond_task = Task(
        description=(
            f"Using the classification and retrieved knowledge base articles, draft a "
            f"customer-facing response to:\nSubject: {subject}\nMessage: {message}\n\n"
            "Be empathetic, clear, and concise. Ground your answer in the retrieved articles."
        ),
        expected_output="A complete, ready-to-send customer support reply.",
        agent=responder_agent,
        context=[classify_task, retrieve_task]
    )

    escalate_task = Task(
        description=(
            "Review the classification, retrieved knowledge, and drafted response. "
            "Decide if this can be auto-sent or must be escalated to a human. "
            "Escalate if: confidence is low, the issue involves a refund dispute, "
            "legal concerns, a distressed/angry customer, or no good KB match was found.\n\n"
            "Respond in this exact format:\n"
            "ESCALATE: yes/no\n"
            "REASON: <one line reason>"
        ),
        expected_output="ESCALATE: yes/no followed by REASON: <reason>",
        agent=escalation_agent,
        context=[classify_task, retrieve_task, respond_task]
    )

    crew = Crew(
        agents=[classifier_agent, retriever_agent, responder_agent, escalation_agent],
        tasks=[classify_task, retrieve_task, respond_task, escalate_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return {
        "classification": classify_task.output.raw if classify_task.output else None,
        "retrieved_context": retrieve_task.output.raw if retrieve_task.output else None,
        "draft_response": respond_task.output.raw if respond_task.output else None,
        "escalation_review": escalate_task.output.raw if escalate_task.output else None,
    }


if __name__ == "__main__":
    test_ticket = process_ticket(
        subject="Refund request",
        message="I was charged again this month even though I cancelled my subscription 3 weeks ago. This is the second time this has happened and I'm furious."
    )
    print("\n\n=== FINAL RESULT ===")
    for k, v in test_ticket.items():
        print(f"\n--- {k} ---\n{v}")
        