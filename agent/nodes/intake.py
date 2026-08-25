# agent/nodes/intake.py

from typing import Any, Dict

from agent.state import ClaimState


def intake_node(state: ClaimState) -> Dict[str, Any]:
    raw_input = state.get("raw_input", "").strip()

    if not raw_input:
        return {
            "error": "Claim input cannot be empty.",
            "current_step": "intake",
        }

    return {
        "raw_input": raw_input,
        "current_step": "intake_completed",
    }