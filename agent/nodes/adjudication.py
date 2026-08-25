from typing import Any, Dict

from agent.state import ClaimState


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

    requested_amount = float(
        claim_data.get(
            "requested_amount",
            0,
        )
    )

    room_rent = calculation.get(
        "room_rent",
        {},
    )

    deduction = float(
        room_rent.get(
            "room_rent_deduction",
            0,
        )
    )

    # Calculate eligible claim amount
    calculated_amount = max(
        0.0,
        requested_amount - deduction,
    )

    risk_level = fraud.get(
        "risk_level",
        "LOW",
    )

    requires_review = (
        risk_level == "HIGH"
        or clinical.get(
            "requires_review",
            False,
        )
    )

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

    # Build deduction details
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