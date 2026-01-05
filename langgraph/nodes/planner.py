from langgraph.state import AgentState
from models.llm import LocalLLM
from models.prompts import get_system_prompt
from api.schemas import Remediation, Provenance
from typing import Dict, Any
import json
import uuid

llm = LocalLLM()

def plan_remediation(state: AgentState) -> Dict[str, Any]:
    """
    Node: Planner
    Goal: Generate a structured remediation plan.
    """
    print("--- NODE: PLANNING REMEDIATION ---")
    alert = state["alert"]
    analysis = state["normalized_summary"]
    context = state["context"]
    
    system_prompt = get_system_prompt("planner")
    user_prompt = f"""
    Analyst Findings: {analysis}
    Original Alert: {alert.summary}
    Severity: {alert.severity}
    
    Context:
    {json.dumps(context, default=str)}
    
    Generate a strict JSON remediation plan based on the findings and context.
    """
    
    # Call LLM
    response_text = llm.generate_with_system_prompt(system_prompt, user_prompt)
    
    # Parse JSON (Basic cleanup)
    try:
        # Extract JSON if wrapped in markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "{" in response_text:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            response_text = response_text[start:end]
            
        plan_dict = json.loads(response_text)
        
        # Construct Remediation Object
        # We mock provenance matching for MVP
        provenance = []
        if context:
             provenance.append(Provenance(
                 doc_id=context[0].get("metadata", {}).get("source", "unknown"),
                 chunk_id="chk-1",
                 score=0.9
             ))
             
        remediation = Remediation(
            action_id=str(uuid.uuid4()),
            alert_id=alert.alert_id,
            title=plan_dict.get("title", "Remediation Plan"),
            steps=plan_dict.get("steps", []),
            confidence=plan_dict.get("confidence", 0.5),
            provenance=provenance,
            model_version="gpt4all-v1",
            prompt_hash="hash-123", # In prod, compute this
            policy_verdict="PENDING"
        )
        
        return {"remediation": remediation}
        
    except Exception as e:
        print(f"Error parsing remediation plan: {e}")
        # Return nothing or error state
        return {"next_step": "ERROR"}
