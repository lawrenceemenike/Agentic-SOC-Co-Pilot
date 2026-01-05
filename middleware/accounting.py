from sqlalchemy.orm import Session
from infra.db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from typing import Dict, Any

# DB Model for Token Usage
class TokenUsage(Base):
    __tablename__ = "token_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent = Column(String)
    model = Column(String)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    cost_estimate = Column(Float)

from finops.budget import BudgetPolicy
from finops.anomaly import AnomalyDetector
from fastapi import HTTPException
from infra.observability import TOKEN_USAGE_TOTAL, BUDGET_SPEND_DAILY

class TokenAccountant:
    def __init__(self, db: Session):
        self.db = db
        # Cost per 1k tokens (example)
        self.cost_per_1k = 0.002 
        
        # Initialize FinOps controls
        # In a real app, these might be singletons injected via dependency injection
        self.budget_policy = BudgetPolicy()
        self.anomaly_detector = AnomalyDetector()

    def check_and_log(self, agent: str, metadata: Dict[str, Any]):
        """
        Checks budget/anomalies BEFORE or AFTER execution.
        Ideally, we check budget before (if we can estimate) or after (to stop future calls).
        Here we do it after to record the actual spend and block *next* time if needed,
        or we could throw an error now if it was a massive spike.
        """
        prompt_tokens = metadata.get("prompt_tokens", 0)
        completion_tokens = metadata.get("completion_tokens", 0)
        total = prompt_tokens + completion_tokens
        cost = (total / 1000) * self.cost_per_1k

        # 1. Anomaly Detection
        if self.anomaly_detector.is_anomaly(total):
            # Log it, maybe alert. For now, we just print/log.
            print(f"ANOMALY DETECTED: Token spike of {total} tokens for agent {agent}")
            # We could raise an exception to block the result, but usually we just alert.

        # 2. Budget Check
        # We check if *adding* this cost would break the bank.
        budget_result = self.budget_policy.check_budget(cost)
        if not budget_result["allowed"]:
            raise HTTPException(status_code=429, detail=f"Budget Exceeded: {budget_result['reason']}")

        # 3. Record Spend
        self.budget_policy.record_spend(cost)
        
        # Metrics Update
        TOKEN_USAGE_TOTAL.labels(model=metadata.get("model_version", "unknown"), type="prompt").inc(prompt_tokens)
        TOKEN_USAGE_TOTAL.labels(model=metadata.get("model_version", "unknown"), type="completion").inc(completion_tokens)
        BUDGET_SPEND_DAILY.set(self.budget_policy.current_spend)

        # 4. Persist to DB
        usage = TokenUsage(
            agent=agent,
            model=metadata.get("model_version", "unknown"),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            cost_estimate=cost
        )
        self.db.add(usage)
        self.db.commit()
