# Secure Agentic SOC Co-Pilot

An **Agentic Security Operations Center (SOC)** assistant designed to run **entirely locally** (air-gapped) with strict **FinOps** and **Security Governance** controls.

This project demonstrates how to build a "Safe & Solvent" AI system that can autonomously analyze threats, propose remediations, and adhere to strict financial and policy boundaries.

---

## 🏗️ Architecture

The system is built on a **Micro-Agent Architecture** orchestrated by **LangGraph**. It follows a "Brain-in-a-Box" design where data never leaves the local perimeter.

### Core Components
*   **Orchestrator**: `LangGraph` state machine managing the lifecycle of an alert (`Retrieve` -> `Analyze` -> `Plan` -> `Verify`).
*   **API Gateway**: `FastAPI` handling alert ingestion (Webhooks) with strict Pydantic validation and rate limiting.
*   **Memory**:
    *   **Short-Term**: `Redis` for agent state, rate limits, and user sessions.
    *   **Long-Term**: `ChromaDB` (Vector Store) for RAG (Playbooks, Threat Intel).
*   **Inference Engine**: `GPT4All` running quantized local models (`orca-mini-3b`) on CPU.
*   **Observability**: `Prometheus` & `Grafana` for real-time metrics (Latency, Cost, Security Violations).

### The Agent Graph
1.  **Context Retriever**: Fetches relevant SOPs and historical incidents using **Hybrid Search** (Vector + BM25).
2.  **Analyst Agent**: A Tier-3 SOC expert that correlates alerts with context to assess true risk and map to MITRE ATT&CK.
3.  **Planner Agent**: Generates structured, step-by-step remediation plans (JSON).
4.  **Verifier Agent**: A "Department of Internal Affairs" that audits the plan for safety before it reaches a human.

---

## 🛡️ Security Engineering

Security is not an afterthought; it is the primary constraint of the system. We implement a **Defense-in-Depth** strategy:

### 1. Input/Output Guardrails (`verifier.py`)
*   **Policy Engine**: Regex-based blocking of dangerous commands (`rm -rf`, `sudo`, `curl`).
*   **Semantic Verification**: A Cross-Encoder model checks **Groundedness**—ensuring the AI's plan is actually supported by the retrieved context (preventing hallucinations).
*   **LLM Guardrail**: A dedicated "Compliance Officer" LLM that reviews plans for subtle policy violations, PII leakage, and professionalism.

### 2. Human-in-the-Loop (`approval.py`)
*   **RBAC**: Strict Role-Based Access Control ensures only authorized `analysts` can approve remediation plans.
*   **No Self-Approval**: The system cryptographically prevents the Agent from approving its own actions.

### 3. Automated Red Teaming (`run_redteam.py`)
*   A CI/CD pipeline step that bombards the system with known adversarial attacks (Prompt Injection, XSS, Jailbreaks) to ensure defenses hold before deployment.

---

## 💰 FinOps & Accounting

To prevent "Bill Shock" and infinite loops, the system treats Compute as Currency.

### 1. The Token Accountant (`accounting.py`)
*   **Middleware**: Sits between the Agent and the Model.
*   **Ledger**: Records every single token generated, the model used, and the estimated cost in USD.

### 2. Budget Policy (`budget.py`)
*   **Hard Limits**: Enforces a strict daily budget (e.g., $5.00).
*   **Circuit Breaker**: If the budget is exceeded, the API returns `429 Too Many Requests` and halts all inference immediately.

### 3. Anomaly Detection (`anomaly.py`)
*   **Statistical Analysis**: Uses Z-Score analysis to detect usage spikes (e.g., an agent entering an infinite loop) and flags them as anomalies.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Docker (for Redis/Grafana)
*   Git

### Installation
1.  **Clone the Repository**
    ```bash
    git clone https://github.com/lawrenceemenike/Agentic-SOC-Co-Pilot.git
    cd Agentic-SOC-Co-Pilot
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start Infrastructure**
    ```bash
    docker-compose up -d
    ```

4.  **Run the API**
    ```bash
    uvicorn api.main:app --reload
    ```

### Usage
**Ingest an Alert**:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "CrowdStrike",
    "severity": "HIGH",
    "summary": "Suspicious PowerShell execution detected on host DB-01"
  }'
```

**View Dashboard**:
Open `http://localhost:3000` to see the Grafana Security & FinOps Dashboard.

---

## 🧪 Testing

Run the full suite, including the Red Team attack simulation:
```bash
pytest
```
