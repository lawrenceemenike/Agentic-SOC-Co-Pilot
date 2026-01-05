from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BudgetPolicy:
    def __init__(self):
        # Limits in USD
        self.soft_limit_daily = 10.0
        self.hard_limit_daily = 50.0
        self.current_spend = 0.0 # In production, fetch from DB/Redis

    def check_budget(self, estimated_cost: float) -> Dict[str, Any]:
        """
        Checks if the call is within budget.
        """
        projected_spend = self.current_spend + estimated_cost
        
        if projected_spend > self.hard_limit_daily:
            logger.error(f"Hard budget limit exceeded. Spend: {projected_spend}, Limit: {self.hard_limit_daily}")
            return {"allowed": False, "reason": "Hard budget limit exceeded"}
            
        if projected_spend > self.soft_limit_daily:
            logger.warning(f"Soft budget limit exceeded. Spend: {projected_spend}, Limit: {self.soft_limit_daily}")
            # We allow but log warning / trigger alert
            return {"allowed": True, "warning": "Soft budget limit exceeded"}
            
        return {"allowed": True}

    def record_spend(self, cost: float):
        self.current_spend += cost
