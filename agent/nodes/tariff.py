from typing import Any, Dict

from agent.state import ClaimState
from tools.tariff import search_tariff


def tariff_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})

    procedure = claim_data.get("procedure")
    hospital_id = claim_data.get("hospital_id")

    if not procedure:
        return {
            "tariff_results": {},
            "error": "Procedure is missing from claim data.",
            "current_step": "tariff_failed",
        }

    if not hospital_id:
        return {
            "tariff_results": {},
            "error": "Hospital ID is missing from claim data.",
            "current_step": "tariff_failed",
        }

    try:
        result = search_tariff(
            hospital_id=hospital_id,
            procedure_name=procedure,
        )

        return {
            "tariff_results": result,
            "current_step": "tariff_completed",
        }

    except Exception as exc:
        return {
            "tariff_results": {},
            "error": f"Tariff lookup failed: {exc}",
            "current_step": "tariff_failed",
        }