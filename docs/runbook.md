# Secure Agentic SOC Co-Pilot - Runbook

## 1. System Overview
The SOC Co-Pilot assists analysts by ingesting alerts, retrieving context, and proposing remediation. It enforces strict human-in-the-loop approval.

## 2. Maintenance Procedures

### 2.1 Model Rotation
To update the local LLM model:
1. Download the new GGUF model to `models/`.
2. Update `models/llm.py` default model path or environment variable `MODEL_PATH`.
3. Restart the service: `docker-compose restart api`.

### 2.2 Memory Flush (Redis)
To clear short-term context (e.g., after an incident is closed):
```bash
docker-compose exec redis redis-cli FLUSHDB
```

### 2.3 Re-indexing Knowledge
To update the vector store:
1. Ingest new documents via the `MemoryGovernance` API (not exposed in MVP, use script).
2. Or wipe and rebuild: Stop services, delete `chroma_data/`, restart.

## 3. Incident Response

### 3.1 Policy Violation Alert
If `prompt_injection_attempts_total` spikes:
1. Check Grafana "Security KPIs" dashboard.
2. Identify the source IP/User from logs (search for `event_type="unauthorized_approval_attempt"` or `policy_verdict="FAIL"`).
3. Block the source at the API Gateway or Firewall.

### 3.2 Agent Hallucination
If confidence is high but recommendation is wrong:
1. Flag the alert ID.
2. Review the `provenance` in the audit log.
3. If a specific playbook caused it, remove/update it in ChromaDB.
