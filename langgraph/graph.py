from langgraph.graph import StateGraph, END
from langgraph.state import AgentState
from langgraph.nodes.retriever import retrieve_context
from langgraph.nodes.analyst import analyze_alert
from langgraph.nodes.planner import plan_remediation
from langgraph.nodes.verifier import verify_plan

# Define the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("retrieve", retrieve_context)
workflow.add_node("analyze", analyze_alert)
workflow.add_node("plan", plan_remediation)
workflow.add_node("verify", verify_plan)

# Define Edges
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "analyze")
workflow.add_edge("analyze", "plan")
workflow.add_edge("plan", "verify")
workflow.add_edge("verify", END)

# Compile
app = workflow.compile()

async def process_alert(alert):
    """
    Entry point for the API to trigger the graph.
    """
    # Initialize state
    initial_state = {
        "alert": alert,
        "context": [],
        "normalized_summary": None,
        "remediation": None,
        "verification_result": None,
        "next_step": "start"
    }
    
    # Run the graph
    # Note: In a real async app, use ainvoke or stream
    # For MVP with synchronous local models, we use invoke
    result = app.invoke(initial_state)
    
    return result
