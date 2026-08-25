# guardrails/input_guard.py

from typing import Any, Dict


class InputGuard:
    """Validates incoming ClaimGuard claim requests."""

    MAX_INPUT_LENGTH = 50000

    def validate(
        self,
        raw_input: str,
    ) -> Dict[str, Any]:

        errors = []

        if not raw_input or not raw_input.strip():
            errors.append(
                "Claim input cannot be empty."
            )

        if len(raw_input) > self.MAX_INPUT_LENGTH:
            errors.append(
                "Claim input exceeds the maximum allowed length."
            )

        blocked_patterns = [
            "ignore previous instructions",
            "ignore all previous instructions",
            "system prompt",
            "reveal your instructions",
        ]

        normalized_input = raw_input.lower()

        for pattern in blocked_patterns:
            if pattern in normalized_input:
                errors.append(
                    "Potential prompt injection detected."
                )
                break

        return {
            "valid": not errors,
            "errors": errors,
        }


input_guard = InputGuard()