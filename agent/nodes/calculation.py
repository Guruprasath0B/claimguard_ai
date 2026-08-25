# agent/nodes/calculation.py

from typing import Any, Dict

from agent.state import ClaimState
from tools.room_rent import (
    calculate_room_rent_deduction,
    calculate_proportional_deduction,
)


def calculation_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})

    sum_insured = claim_data.get("sum_insured", 0)
    room_rent = claim_data.get("room_rent_per_day")
    days = claim_data.get("hospitalization_days", 1)
    cap_percent = claim_data.get(
        "room_rent_cap_percent",
        1.0,
    )

    if not room_rent:
        return {
            "calculation_results": {},
            "current_step": "calculation_skipped",
        }

    try:
        room_result = calculate_room_rent_deduction(
            sum_insured=float(sum_insured),
            room_rent_per_day=float(room_rent),
            days=int(days),
            room_rent_cap_percent=float(cap_percent),
        )

        return {
            "calculation_results": {
                "room_rent": room_result,
            },
            "current_step": "calculation_completed",
        }

    except Exception as exc:
        return {
            "calculation_results": {},
            "error": f"Claim calculation failed: {exc}",
            "current_step": "calculation_failed",
        }