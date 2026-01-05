from typing import TypedDict, List, Dict, Any, Optional, Annotated
from api.schemas import Alert, Remediation
import operator

class AgentState(TypedDict):
    # The raw input alert
    alert: Alert
    
    # Normalized/Enriched data
    normalized_summary: Optional[str]
    
    # Retrieved context from VectorDB/Tools
    context: Annotated[List[Dict[str, Any]], operator.add]
    
    # The proposed plan
    remediation: Optional[Remediation]
    
    # Verification results
    verification_result: Optional[Dict[str, Any]]
    
    # Human feedback
    human_feedback: Optional[str]
    
    # Flow control
    next_step: str
    retry_count: int
