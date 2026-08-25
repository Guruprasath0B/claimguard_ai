# agent/nodes/memory.py

from typing import Any, Dict

from agent.state import ClaimState
from memory.patient_history import patient_history_service


def memory_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})

    patient_id = claim_data.get(
        "patient_identifier"
    )

    if not patient_id:
        return {
            "patient_history": [],
            "current_step": "memory_skipped",
        }

    try:
        history = (
            patient_history_service.get_relevant_history(
                patient_id=patient_id,
                query=(
                    f"Previous claims related to "
                    f"{claim_data.get('diagnosis', '')}"
                ),
            )
        )

        return {
            "patient_id": patient_id,
            "patient_history": history,
            "current_step": "memory_completed",
        }

    except Exception as exc:
        return {
            "patient_history": [],
            "error": f"Patient memory lookup failed: {exc}",
            "current_step": "memory_failed",
        }