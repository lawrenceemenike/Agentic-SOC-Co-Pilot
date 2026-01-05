import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="SOC Co-Pilot", layout="wide")

st.title("🛡️ Secure Agentic SOC Co-Pilot")

# Sidebar for role simulation
role = st.sidebar.selectbox("Simulate Role", ["analyst", "admin", "agent", "viewer"])

# Mock Alert Data (in real app, fetch from API/DB)
alerts = [
    {
        "alert_id": "a-123",
        "severity": "HIGH",
        "summary": "Multiple failed logins from IP 1.2.3.4",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "PENDING_APPROVAL",
        "remediation": {
            "action_id": "act-001",
            "title": "Block IP 1.2.3.4",
            "steps": ["Verify source", "Block on Firewall"],
            "confidence": 0.85
        }
    }
]

st.header("🚨 Active Alerts")

for alert in alerts:
    with st.expander(f"{alert['severity']} - {alert['summary']} ({alert['status']})"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Alert Details")
            st.json(alert)
            
        with col2:
            st.subheader("Proposed Remediation")
            st.write(f"**Action:** {alert['remediation']['title']}")
            st.write("**Steps:**")
            for step in alert['remediation']['steps']:
                st.write(f"- {step}")
            st.write(f"**Confidence:** {alert['remediation']['confidence']}")
            
            # Approval Buttons
            if alert['status'] == "PENDING_APPROVAL":
                comment = st.text_input("Comments", key=f"comment_{alert['alert_id']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Approve", key=f"approve_{alert['alert_id']}"):
                        # Call API
                        try:
                            headers = {"x-user-role": role}
                            payload = {
                                "action_id": alert['remediation']['action_id'],
                                "decision": "APPROVE",
                                "comments": comment
                            }
                            # Assuming API is running on localhost:8000
                            # res = requests.post("http://localhost:8000/approve", json=payload, headers=headers)
                            # Mocking response for UI demo without running backend
                            if role in ["analyst", "admin"]:
                                st.success("Approved successfully!")
                            else:
                                st.error("Unauthorized: Only analysts can approve.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
                with c2:
                    if st.button("❌ Reject", key=f"reject_{alert['alert_id']}"):
                        if role in ["analyst", "admin"]:
                            st.warning("Rejected.")
                        else:
                            st.error("Unauthorized.")
