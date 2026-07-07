from crewai.tools import BaseTool
from app.services.rag_service import retrieve


class KnowledgeBaseSearchTool(BaseTool):
    name: str = "knowledge_base_search"
    description: str = (
        "Searches the company support knowledge base for relevant articles "
        "given a customer's issue description. Returns the top matching "
        "articles with their category, title, and content."
    )

    def _run(self, query: str) -> str:
        results = retrieve(query, k=3)
        if not results:
            return "No relevant knowledge base articles found."

        formatted = []
        for r in results:
            formatted.append(
                f"[{r['category'].upper()}] {r['title']}\n{r['content']}"
            )
        return "\n\n".join(formatted)