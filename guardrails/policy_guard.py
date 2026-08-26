from typing import Any, Dict, List


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """Safely convert a value to float."""
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class PolicyGuard:
    """Ensures claim decisions are grounded in retrieved policy rules."""

    def validate(
        self,
        claim_data: Dict[str, Any],
        policy_clauses: List[Dict[str, Any]],
        adjudication: Dict[str, Any],
    ) -> Dict[str, Any]:

        errors = []

        if not policy_clauses:
            errors.append(
                "No policy clauses were retrieved."
            )

        if not claim_data:
            errors.append(
                "Claim data is missing."
            )

        if not adjudication:
            errors.append(
                "Adjudication result is missing."
            )

        # ----------------------------------------------------
        # SAFE NUMERIC CONVERSION
        # ----------------------------------------------------

        approved_amount = safe_float(
            adjudication.get(
                "approved_amount_inr"
            )
        )

        requested_amount = safe_float(
            claim_data.get(
                "requested_amount"
            )
        )

        sum_insured = safe_float(
            claim_data.get(
                "sum_insured"
            )
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if approved_amount > requested_amount:
            errors.append(
                "Approved amount exceeds requested amount."
            )

        if approved_amount > sum_insured:
            errors.append(
                "Approved amount exceeds sum insured."
            )

        return {
            "valid": not errors,
            "errors": errors,
        }


policy_guard = PolicyGuard()