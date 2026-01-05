# Threat Model & Data Flow

## Threat Flow Diagram

```mermaid
graph TD
    Attacker[External Attacker] -->|Malicious Payload| API[API Gateway]
    API -->|Sanitized Alert| Agent[Agent Orchestrator]
    
    subgraph "Secure Zone"
        Agent -->|Query| VectorDB[(ChromaDB)]
        Agent -->|Prompt| LLM[Local LLM]
        LLM -->|Raw Output| Verifier[Output Verifier]
        Verifier -->|Verified Action| Approval[Approval Gate]
    end
    
    subgraph "Human Layer"
        Analyst((Analyst)) -->|Approve/Reject| Approval
        Admin((Admin)) -->|Audit| Logs[(Audit Logs)]
    end
    
    Attacker -.->|Prompt Injection| LLM
    VectorDB -.->|Poisoned Doc| LLM
    
    style Verifier fill:#f96,stroke:#333,stroke-width:2px
    style Approval fill:#9f6,stroke:#333,stroke-width:2px
```

## Attack Surfaces & Mitigations

| Surface | Threat | Mitigation |
|---------|--------|------------|
| **Ingress** | Malformed JSON, Overload | Strict Schema, Rate Limiting |
| **Prompting** | Injection, Jailbreak | Immutable System Prompt, Input Sanitization, Output Verifier |
| **Retrieval** | Poisoned Context | Source Allowlist, Write Governance |
| **Execution** | Unauthorized Action | RBAC, Human Approval, No Auto-Execute |
| **Logs** | PII Leakage | Redaction, Hashing |
