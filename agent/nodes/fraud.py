# agent/nodes/fraud.py

from typing import Any, Dict

from agent.state import ClaimState
from tools.fraud import detect_fraud_anomalies


def fraud_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})

    try:
        fraud_result = detect_fraud_anomalies(
            claim_data
        )

        return {
            "fraud_assessment": fraud_result,
            "current_step": "fraud_completed",
        }

    except Exception as exc:
        return {
            "fraud_assessment": {
                "risk_level": "HIGH",
                "anomaly_flags": [
                    "Fraud analysis failed."
                ],
            },
            "error": f"Fraud analysis failed: {exc}",
            "current_step": "fraud_failed",
        }