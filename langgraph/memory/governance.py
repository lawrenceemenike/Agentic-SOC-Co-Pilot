from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from langgraph.memory.vector_store import VectorStore

class MemoryGovernance:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        # In-memory pending queue for MVP. In production, use Redis or DB.
        self.pending_writes: Dict[str, Dict[str, Any]] = {}

    def propose_memory_addition(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Proposes a new memory addition. Returns a proposal ID.
        The addition is NOT committed to the vector store until approved.
        """
        proposal_id = str(uuid.uuid4())
        self.pending_writes[proposal_id] = {
            "content": content,
            "metadata": metadata,
            "status": "PENDING",
            "timestamp": datetime.utcnow().isoformat()
        }
        return proposal_id

    def approve_memory_addition(self, proposal_id: str, approver_id: str):
        """
        Approves a pending memory addition and commits it to the vector store.
        """
        proposal = self.pending_writes.get(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
        
        if proposal["status"] != "PENDING":
            raise ValueError(f"Proposal is already {proposal['status']}")

        # Commit to vector store
        # Generate a deterministic doc_id or use proposal_id
        doc_id = f"doc-{proposal_id}"
        self.vector_store.add_document(doc_id, proposal["content"], proposal["metadata"])
        
        proposal["status"] = "APPROVED"
        proposal["approver"] = approver_id
        proposal["approved_at"] = datetime.utcnow().isoformat()

    def reject_memory_addition(self, proposal_id: str, rejector_id: str):
        """
        Rejects a pending memory addition.
        """
        proposal = self.pending_writes.get(proposal_id)
        if not proposal:
            raise ValueError("Proposal not found")
            
        proposal["status"] = "REJECTED"
        proposal["rejector"] = rejector_id
        proposal["rejected_at"] = datetime.utcnow().isoformat()
