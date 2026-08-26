from typing import Any, Dict

from agent.state import ClaimState
from tools.room_rent import (
    calculate_room_rent_deduction,
    calculate_proportional_deduction,
)


def calculation_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})

    # --------------------------------------------------------
    # INPUTS
    # --------------------------------------------------------

    sum_insured = claim_data.get("sum_insured")
    room_rent = claim_data.get("room_rent_per_day")
    days = claim_data.get("hospitalization_days", 1)

    # Default policy cap = 1% of Sum Insured
    cap_percent = claim_data.get(
        "room_rent_cap_percent",
        1.0,
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if room_rent is None:
        return {
            "calculation_results": {},
            "error": "Room rent per day is missing.",
            "current_step": "calculation_failed",
        }

    if sum_insured is None:
        return {
            "calculation_results": {},
            "error": "Sum insured is missing.",
            "current_step": "calculation_failed",
        }

    try:
        sum_insured = float(sum_insured)
        room_rent = float(room_rent)
        days = int(days or 1)
        cap_percent = float(
            cap_percent if cap_percent is not None else 1.0
        )

    except (TypeError, ValueError) as exc:
        return {
            "calculation_results": {},
            "error": (
                f"Invalid calculation input: {exc}"
            ),
            "current_step": "calculation_failed",
        }

    # --------------------------------------------------------
    # ROOM RENT CALCULATION
    # --------------------------------------------------------

    try:
        room_result = calculate_room_rent_deduction(
            sum_insured=sum_insured,
            room_rent_per_day=room_rent,
            days=days,
            room_rent_cap_percent=cap_percent,
        )

        if not room_result:
            return {
                "calculation_results": {},
                "error": (
                    "Room rent calculation returned "
                    "an empty response."
                ),
                "current_step": "calculation_failed",
            }

        # ----------------------------------------------------
        # NORMALIZE POSSIBLE NULL VALUES
        # ----------------------------------------------------

        if room_result.get("room_rent_deduction") is None:
            room_result["room_rent_deduction"] = 0.0

        if room_result.get("eligible_room_rent") is None:
            room_result["eligible_room_rent"] = (
                sum_insured * cap_percent
            )

        if room_result.get("actual_room_rent") is None:
            room_result["actual_room_rent"] = (
                room_rent * days
            )

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "calculation_results": {
                "room_rent": room_result,
            },
            "current_step": "calculation_completed",
        }

    except Exception as exc:
        return {
            "calculation_results": {},
            "error": (
                f"Claim calculation failed: {exc}"
            ),
            "current_step": "calculation_failed",
        }