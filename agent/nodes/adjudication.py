from typing import Any, Dict

from agent.state import ClaimState


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def adjudication_node(state: ClaimState) -> Dict[str, Any]:

    claim_data = state.get("claim_data", {})
    calculation = state.get(
        "calculation_results",
        {},
    )
    fraud = state.get(
        "fraud_assessment",
        {},
    )
    clinical = state.get(
        "clinical_assessment",
        {},
    )

    # --------------------------------------------------------
    # REQUESTED AMOUNT
    # --------------------------------------------------------

    requested_amount = safe_float(
        claim_data.get("requested_amount"),
        0.0,
    )

    # --------------------------------------------------------
    # ROOM RENT
    # --------------------------------------------------------

    room_rent = calculation.get(
        "room_rent",
        {},
    )

    if not isinstance(room_rent, dict):
        room_rent = {}

    deduction = safe_float(
        room_rent.get("room_rent_deduction"),
        0.0,
    )

    # --------------------------------------------------------
    # CALCULATED ELIGIBLE AMOUNT
    # --------------------------------------------------------

    calculated_amount = max(
        0.0,
        requested_amount - deduction,
    )

    # --------------------------------------------------------
    # FRAUD
    # --------------------------------------------------------

    risk_level = fraud.get(
        "risk_level",
        "LOW",
    )

    if risk_level is None:
        risk_level = "LOW"

    # --------------------------------------------------------
    # CLINICAL REVIEW
    # --------------------------------------------------------

    requires_review = (
        risk_level == "HIGH"
        or bool(
            clinical.get(
                "requires_review",
                False,
            )
        )
    )

    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    if requires_review:

        status = "QUERY_RAISED"
        approved_amount = 0.0

    elif calculated_amount <= 0:

        status = "REJECTED"
        approved_amount = 0.0

    elif calculated_amount < requested_amount:

        status = "PARTIAL_APPROVAL"
        approved_amount = calculated_amount

    else:

        status = "APPROVED"
        approved_amount = calculated_amount

    # --------------------------------------------------------
    # DEDUCTIONS
    # --------------------------------------------------------

    deductions = []

    if deduction > 0:

        deductions.append(
            {
                "category": "ROOM_RENT",
                "type": "ROOM_RENT",
                "description": (
                    "Room rent exceeded eligible policy limit"
                ),
                "amount_inr": deduction,
                "clause_reference": "POL-ROOM-001",
            }
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    result = {
        "claim_status": status,
        "requested_amount_inr": requested_amount,
        "calculated_eligible_amount_inr": calculated_amount,
        "approved_amount_inr": approved_amount,
        "deductions": deductions,
        "total_deduction_inr": deduction,
        "requires_manual_review": requires_review,
        "fraud_risk": risk_level,
    }

    return {
        "adjudication_result": result,
        "current_step": "adjudication_completed",
    }