# guardrails/output_validator.py

from typing import Any, Dict

from schemas.decision import ClaimDecision


class OutputValidator:
    """Validates the final ClaimGuard decision."""

    def validate(
        self,
        output: Dict[str, Any],
    ) -> Dict[str, Any]:

        try:
            decision = ClaimDecision.model_validate(
                output
            )

            if (
                decision.approved_amount_inr
                > decision.requested_amount_inr
            ):
                return {
                    "valid": False,
                    "errors": [
                        "Approved amount cannot exceed "
                        "requested amount."
                    ],
                }

            if decision.approved_amount_inr < 0:
                return {
                    "valid": False,
                    "errors": [
                        "Approved amount cannot be negative."
                    ],
                }

            return {
                "valid": True,
                "errors": [],
                "validated_output": (
                    decision.model_dump()
                ),
            }

        except Exception as exc:
            return {
                "valid": False,
                "errors": [
                    f"Output validation failed: {exc}"
                ],
            }


output_validator = OutputValidator()