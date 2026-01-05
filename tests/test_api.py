from fastapi.testclient import TestClient
from api.main import app
from api.security import sanitize_input
import pytest

client = TestClient(app)

def test_sanitize_input():
    # Test control char removal
    assert sanitize_input("Hello\x00World") == "HelloWorld"
    # Test HTML stripping
    assert sanitize_input("<script>alert(1)</script>Hello") == "alert(1)Hello"
    # Test whitespace normalization
    assert sanitize_input("  Hello   World  ") == "Hello World"

def test_ingest_valid_alert():
    payload = {
        "alert_id": "test-1",
        "source": "siem",
        "severity": "HIGH",
        "summary": "Test Alert",
        "raw_payload_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", # Empty string hash for testing
        "timestamp": "2023-01-01T00:00:00Z"
    }
    # We need a real hash for the payload we send? 
    # The API computes the hash of the *received* body. 
    # The payload field `raw_payload_hash` is what the SIEM *claims* it is, or maybe we generate it?
    # In the PRD: "Log incoming raw event hash (sha256)".
    # In the schema: `raw_payload_hash` is a required field.
    # Let's assume the SIEM sends it.
    
    response = client.post("/ingest", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "accepted"

def test_ingest_malformed_json():
    response = client.post("/ingest", content="{invalid_json")
    assert response.status_code == 400

def test_ingest_schema_violation():
    payload = {
        "alert_id": "test-1",
        # Missing source
        "severity": "HIGH",
        "summary": "Test Alert",
        "raw_payload_hash": "sha256:...",
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 422

def test_ingest_control_chars_in_summary():
    payload = {
        "alert_id": "test-1",
        "source": "siem",
        "severity": "HIGH",
        "summary": "Test\x00Alert", # Should be sanitized or rejected? 
        # The schema validator `no_control_chars` raises ValueError.
        # The API `sanitize_input` is called *before* validation in `api/main.py`.
        # So it should pass validation after sanitization.
        "raw_payload_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 201
    # We can't easily check the sanitized value without inspecting logs or return value if it echoed back.
    # But 201 means it passed validation.
