from langgraph.agents.verifier import OutputVerifier, PolicyEngine, LLMGuardrail
from models.local_adapter import LocalAdapter
from typing import Dict, Any
from infra.observability import POLICY_VIOLATIONS_TOTAL

# Initialize Verifiers
policy_engine = PolicyEngine()
verifier = OutputVerifier(policy_engine)
# We need an adapter for the guardrail
adapter = LocalAdapter() 
guardrail = LLMGuardrail(adapter)

def verify_plan(state: AgentState) -> Dict[str, Any]:
    """
    Node: Verifier
    Goal: Check if the plan is safe and grounded.
    """
    print("--- NODE: VERIFYING PLAN ---")
    remediation = state["remediation"]
    context = state["context"]
    
    if not remediation:
        return {"next_step": "END"}
        
    # 1. Convert plan to text for verification
    plan_text = f"{remediation.title}\n" + "\n".join(remediation.steps)
    
    # 2. Run OutputVerifier (Regex + CrossEncoder)
    verdict = verifier.verify(plan_text, context)
    
    # 3. Run LLM Guardrail (The new pattern we added)
    # We check the *steps* specifically
    guardrail_result = guardrail.check(plan_text)
    
    final_verdict = "PASS"
    if verdict["verdict"] == "FAIL":
        final_verdict = "FAIL"
        POLICY_VIOLATIONS_TOTAL.labels(policy_type="regex_verifier").inc()
    elif guardrail_result["verdict"] == "FAIL":
        final_verdict = "FAIL"
        POLICY_VIOLATIONS_TOTAL.labels(policy_type="llm_guardrail").inc()
        
    # Update Remediation object
    remediation.policy_verdict = final_verdict
    
    return {
        "verification_result": {
            "verifier": verdict,
            "guardrail": guardrail_result
        },
        "remediation": remediation
    }
