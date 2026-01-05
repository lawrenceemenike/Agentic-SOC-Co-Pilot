from langgraph.state import AgentState
from models.llm import LocalLLM
from models.prompts import get_system_prompt
from typing import Dict, Any

# Initialize LLM
llm = LocalLLM()

def analyze_alert(state: AgentState) -> Dict[str, Any]:
    """
    Node: Analyst
    Goal: Analyze the alert and context to understand the threat.
    """
    print("--- NODE: ANALYZING ALERT ---")
    alert = state["alert"]
    context = state["context"]
    
    # Prepare context string
    context_str = "\n".join([f"- {c['content']}" for c in context])
    
    # Construct Prompt
    system_prompt = get_system_prompt("analyst")
    user_prompt = f"""
    Alert: {alert.json()}
    
    Context:
    {context_str}
    
    Task: Perform a deep-dive analysis. Is this a False Positive? Map to MITRE ATT&CK.
    """
    
    # Call LLM
    analysis = llm.generate_with_system_prompt(system_prompt, user_prompt)
    
    return {"normalized_summary": analysis}
