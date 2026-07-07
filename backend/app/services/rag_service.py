import json
import os
import chromadb
from chromadb.utils import embedding_functions

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KB_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

# Use a free, local embedding model — no API cost
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)


def build_knowledge_base():
    """Load knowledge_base.json and embed it into ChromaDB. Run once, or whenever KB changes."""
    with open(KB_PATH, "r") as f:
        docs = json.load(f)

    collection = client.get_or_create_collection(
        name="support_kb",
        embedding_function=embedding_fn
    )

    # Clear existing entries to avoid duplicates on rebuild
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.add(
        ids=[doc["id"] for doc in docs],
        documents=[doc["content"] for doc in docs],
        metadatas=[{"category": doc["category"], "title": doc["title"]} for doc in docs]
    )
    print(f"Indexed {len(docs)} knowledge base entries.")
    return collection


def get_collection():
    return client.get_or_create_collection(
        name="support_kb",
        embedding_function=embedding_fn
    )


def retrieve(query: str, k: int = 3):
    """Retrieve top-k relevant KB entries for a given query."""
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=k)

    retrieved = []
    for i in range(len(results["ids"][0])):
        retrieved.append({
            "id": results["ids"][0][i],
            "title": results["metadatas"][0][i]["title"],
            "category": results["metadatas"][0][i]["category"],
            "content": results["documents"][0][i],
            "distance": results["distances"][0][i]
        })
    return retrieved


if __name__ == "__main__":
    build_knowledge_base()
    # Quick test
    test_results = retrieve("customer says password reset email never arrived")
    for r in test_results:
        print(f"- [{r['category']}] {r['title']} (distance: {r['distance']:.3f})")