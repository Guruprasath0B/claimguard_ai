# guardrails/policy_guard.py

from typing import Any, Dict, List


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

        approved_amount = float(
            adjudication.get(
                "approved_amount_inr",
                0,
            )
        )

        requested_amount = float(
            claim_data.get(
                "requested_amount",
                0,
            )
        )

        sum_insured = float(
            claim_data.get(
                "sum_insured",
                0,
            )
        )

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