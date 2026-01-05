from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_approval_rbac_analyst():
    payload = {"action_id": "act-1", "decision": "APPROVE"}
    headers = {"x-user-role": "analyst"}
    response = client.post("/approve", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_approval_rbac_admin():
    payload = {"action_id": "act-1", "decision": "APPROVE"}
    headers = {"x-user-role": "admin"}
    response = client.post("/approve", json=payload, headers=headers)
    assert response.status_code == 200

def test_approval_rbac_agent_denied():
    payload = {"action_id": "act-1", "decision": "APPROVE"}
    headers = {"x-user-role": "agent"}
    response = client.post("/approve", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Unauthorized" in response.json()["detail"]

def test_approval_missing_role():
    payload = {"action_id": "act-1", "decision": "APPROVE"}
    response = client.post("/approve", json=payload)
    assert response.status_code == 401
