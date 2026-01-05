import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

class AuditLogger:
    def __init__(self, service_name: str = "soc-copilot"):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        # In production, configure a file handler or JSON formatter here
        # For now, we rely on the root logger configuration or stdout

    def log_event(self, 
                  event_type: str, 
                  details: Dict[str, Any], 
                  trace_id: Optional[str] = None,
                  user_id: Optional[str] = None):
        """
        Logs a structured audit event.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "service": "soc-copilot",
            "trace_id": trace_id,
            "user_id": user_id,
            "details": details
        }
        self.logger.info(json.dumps(entry))

audit_logger = AuditLogger()
