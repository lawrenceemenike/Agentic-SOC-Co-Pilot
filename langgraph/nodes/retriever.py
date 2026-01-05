from langgraph.state import AgentState
from langgraph.memory.retriever import HybridRetriever
from langgraph.memory.vector_store import VectorStore
from typing import Dict, Any

# Initialize singletons (in prod, use dependency injection)
# We assume Chroma and Redis are running
vector_store = VectorStore()
retriever = HybridRetriever(vector_store)

def retrieve_context(state: AgentState) -> Dict[str, Any]:
    """
    Node: Context Retriever
    Goal: Fetch relevant playbooks and threat intel based on the alert.
    """
    print("--- NODE: RETRIEVING CONTEXT ---")
    alert = state["alert"]
    query = f"{alert.source} {alert.severity} {alert.summary}"
    
    # Fetch docs
    docs = retriever.search(query, k=3)
    
    # Format for state
    context_items = [{"content": doc["content"], "metadata": doc["metadata"]} for doc in docs]
    
    return {"context": context_items}
