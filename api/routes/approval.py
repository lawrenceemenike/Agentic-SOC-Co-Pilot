from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from api.audit import audit_logger

router = APIRouter()

class ApprovalRequest(BaseModel):
    action_id: str
    decision: str # APPROVE or REJECT
    comments: Optional[str] = None

# Mock RBAC
def get_current_user_role(x_user_role: str = Header(None)):
    if not x_user_role:
        raise HTTPException(status_code=401, detail="Missing user role header")
    return x_user_role

@router.post("/approve")
def approve_action(request: ApprovalRequest, role: str = Depends(get_current_user_role)):
    """
    Approves or rejects a remediation action.
    Enforces RBAC: Only 'analyst' or 'admin' can approve. 'agent' cannot.
    """
    if role not in ["analyst", "admin"]:
        audit_logger.log_event("unauthorized_approval_attempt", {
            "action_id": request.action_id,
            "role": role,
            "decision": request.decision
        })
        raise HTTPException(status_code=403, detail="Unauthorized: Only analysts can approve actions")

    # In a real system, we would update the DB state here.
    # For MVP, we just log and return success.
    
    audit_logger.log_event("action_decision", {
        "action_id": request.action_id,
        "role": role,
        "decision": request.decision,
        "comments": request.comments
    })
    
    return {"status": "success", "action_id": request.action_id, "decision": request.decision}
