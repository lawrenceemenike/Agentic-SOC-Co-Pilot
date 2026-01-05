from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from api.schemas import Alert
from api.security import sanitize_input, compute_payload_hash
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



from api.routes import approval
from infra.observability import AGENT_THROUGHPUT, PROMPT_INJECTION_ATTEMPTS, tracer
from opentelemetry.trace import Status, StatusCode

app = FastAPI(title="Secure Agentic SOC Co-Pilot", version="0.1.0")
app.include_router(approval.router)

from fastapi import FastAPI, HTTPException, Request, status, BackgroundTasks, Depends
from api.dependencies import get_api_key, rate_limiter
from langgraph.graph import process_alert
import asyncio

@app.post("/ingest", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limiter)])
async def ingest_alert(request: Request, background_tasks: BackgroundTasks):
    """
    Ingests a raw alert from a SIEM webhook.
    Normalizes, sanitizes, and validates the payload.
    """
    with tracer.start_as_current_span("ingest_alert") as span:
        AGENT_THROUGHPUT.labels(agent="ingest").inc()
        try:
            raw_body = await request.body()
            raw_payload = raw_body.decode("utf-8")
            
            # 1. Compute raw hash for audit
            payload_hash = compute_payload_hash(raw_payload)
            span.set_attribute("payload.hash", payload_hash)
            
            # 2. Parse JSON
            try:
                payload_dict = json.loads(raw_payload)
            except json.JSONDecodeError:
                logger.warning(f"Malformed JSON received. Hash: {payload_hash}")
                span.set_status(Status(StatusCode.ERROR, "Malformed JSON"))
                raise HTTPException(status_code=400, detail="Invalid JSON payload")

            # 3. Sanitize inputs
            if "summary" in payload_dict:
                payload_dict["summary"] = sanitize_input(payload_dict["summary"])
            if "source" in payload_dict:
                payload_dict["source"] = sanitize_input(payload_dict["source"])
                
            payload_dict["raw_payload_hash"] = payload_hash
            
            # 4. Validate against strict schema
            try:
                alert = Alert(**payload_dict)
            except Exception as e:
                logger.error(f"Schema validation failed: {str(e)}")
                span.set_status(Status(StatusCode.ERROR, "Schema Validation Failed"))
                raise HTTPException(status_code=422, detail=f"Schema validation failed: {str(e)}")

            # 5. Log success
            logger.info(f"Alert ingested successfully. ID: {alert.alert_id} Hash: {payload_hash}")
            span.set_status(Status(StatusCode.OK))
            
            # 6. Trigger Agent in Background
            background_tasks.add_task(process_alert, alert)
            
            return {"status": "accepted", "alert_id": alert.alert_id, "hash": payload_hash}

        except HTTPException as he:
            span.set_status(Status(StatusCode.ERROR, str(he.detail)))
            raise he
        except Exception as e:
            logger.error(f"Internal server error during ingestion: {str(e)}")
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
def health_check():
    return {"status": "ok"}
