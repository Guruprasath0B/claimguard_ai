# agent/nodes/privacy.py

from typing import Any, Dict

from agent.state import ClaimState
from privacy.presidio_anonymizer import presidio_anonymizer


def privacy_node(state: ClaimState) -> Dict[str, Any]:
    raw_input = state.get("raw_input", "").strip()

    if not raw_input:
        return {
            "error": "No claim input available for privacy processing.",
            "current_step": "privacy_failed",
        }

    try:
        sanitized_text, token_map = (
            presidio_anonymizer.anonymize(raw_input)
        )

        return {
            "sanitized_input": sanitized_text,
            "presidio_token_map": token_map,
            "current_step": "privacy_completed",
        }

    except Exception as exc:
        return {
            "error": f"Privacy processing failed: {exc}",
            "current_step": "privacy_failed",
        }