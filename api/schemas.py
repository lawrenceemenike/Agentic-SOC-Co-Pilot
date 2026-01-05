from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import re
from datetime import datetime

class Alert(BaseModel):
    alert_id: str = Field(..., min_length=1, max_length=64, description="Unique ID of the alert")
    source: str = Field(..., min_length=1, max_length=64, description="Source system (e.g., SIEM)")
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$", description="Alert severity")
    summary: str = Field(..., min_length=1, max_length=512, description="Brief summary of the alert")
    raw_payload_hash: str = Field(..., pattern="^sha256:[a-f0-9]{64}$", description="SHA256 hash of the raw payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

    @validator('summary')
    def no_control_chars(cls, v):
        if re.search(r'[\x00-\x1f\x7f]', v):
            raise ValueError("Summary contains control characters")
        return v

class Provenance(BaseModel):
    doc_id: str
    chunk_id: str
    score: float

class Remediation(BaseModel):
    action_id: str
    alert_id: str
    type: str = "recommendation"
    title: str
    steps: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    provenance: List[Provenance]
    model_version: str
    prompt_hash: str
    policy_verdict: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
