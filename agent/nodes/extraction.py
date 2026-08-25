from typing import Any, Dict

from agent.state import ClaimState
from ingestion.extractor import claim_extractor


def extraction_node(state: ClaimState) -> Dict[str, Any]:
    try:
        records = [
            {
                "text": state.get(
                    "sanitized_input",
                    "",
                )
            }
        ]

        claim_data = claim_extractor.extract(
            records,
            token_map=state.get(
                "presidio_token_map",
                {},
            ),
        )

        return {
            "claim_data": claim_data,
            "claim_id": claim_data.get("claim_id"),
            "current_step": "extraction_completed",
        }

    except Exception as exc:
        return {
            "error": f"Claim extraction failed: {exc}",
            "current_step": "extraction_failed",
        }