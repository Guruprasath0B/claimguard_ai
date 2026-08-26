from typing import Any, Dict

from agent.state import ClaimState
from memory.patient_history import patient_history_service


def history_save_node(
    state: ClaimState,
) -> Dict[str, Any]:

    claim_data = state.get(
        "claim_data",
        {},
    )

    patient_id = claim_data.get(
        "patient_identifier"
    )

    if not patient_id:
        return {
            "current_step": "history_save_skipped",
        }

    try:

        patient_history_service.save_claim_history(
            patient_id=patient_id,
            claim_data=claim_data,
        )

        return {
            "current_step": "history_saved",
        }

    except Exception as exc:

        return {
            "error": (
                f"Patient history save failed: {exc}"
            ),
            "current_step": "history_save_failed",
        }