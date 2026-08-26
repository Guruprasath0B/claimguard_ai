from typing import Any, Dict

from agent.state import ClaimState
from guardrails.output_validator import output_validator
from guardrails.policy_guard import policy_guard


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    if value is None:
        return default

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def finalization_node(
    state: ClaimState,
) -> Dict[str, Any]:

    claim_data = state.get(
        "claim_data",
        {},
    )

    policy_clauses = state.get(
        "retrieved_policy_clauses",
        [],
    )

    adjudication = state.get(
        "adjudication_result",
        {},
    )

    fraud_assessment = state.get(
        "fraud_assessment",
        {},
    )

    ped_assessment = state.get(
        "ped_assessment",
        {},
    )

    # ======================================================
    # POLICY GUARD
    # ======================================================

    policy_result = policy_guard.validate(
        claim_data=claim_data,
        policy_clauses=policy_clauses,
        adjudication=adjudication,
    )

    if not policy_result.get("valid", False):

        return {
            "final_output": {},
            "guardrails_status": "FAILED",
            "validation_errors": policy_result.get(
                "errors",
                ["Policy validation failed."],
            ),
            "current_step": "finalization_failed",
        }

    # ======================================================
    # AMOUNTS
    # ======================================================

    requested_amount = safe_float(
        adjudication.get(
            "requested_amount_inr",
            claim_data.get(
                "requested_amount",
                0,
            ),
        )
    )

    approved_amount = safe_float(
        adjudication.get(
            "approved_amount_inr",
            0,
        )
    )

    total_deduction = safe_float(
        adjudication.get(
            "total_deduction_inr",
            0,
        )
    )

    # ======================================================
    # PED ASSESSMENT
    # ======================================================

    ped_detected = ped_assessment.get(
        "ped_detected",
        "UNKNOWN",
    )

    # ClaimDecision requires this field to always be boolean.
    # If PED is explicitly absent/negative, claim is not related.
    is_claim_related = ped_assessment.get(
        "is_claim_related",
        False,
    )

    if not isinstance(is_claim_related, bool):
        is_claim_related = False

    waiting_period_status = ped_assessment.get(
        "waiting_period_status",
        "NOT_EVALUATED",
    )

    # ======================================================
    # FINAL OUTPUT
    # ======================================================

    output = {
        "claim_id": claim_data.get(
            "claim_id",
            "UNKNOWN",
        ),

        "patient_identifier_anonymized": (
            "<ANONYMIZED_PATIENT>"
        ),

        "claim_status": adjudication.get(
            "claim_status",
            "QUERY_RAISED",
        ),

        "requested_amount_inr": requested_amount,

        "approved_amount_inr": approved_amount,

        "deductions": adjudication.get(
            "deductions",
            [],
        ),

        "total_deduction_inr": total_deduction,

        # ==================================================
        # PED / WAITING PERIOD
        # ==================================================

        "ped_waiting_period_check": {
            "ped_detected": ped_detected,
            "is_claim_related": is_claim_related,
            "waiting_period_status": waiting_period_status,
        },

        # ==================================================
        # FRAUD
        # ==================================================

        "fraud_risk_assessment": {
            "risk_level": fraud_assessment.get(
                "risk_level",
                "LOW",
            ),
            "anomaly_flags": fraud_assessment.get(
                "anomaly_flags",
                [],
            ),
        },

        # ==================================================
        # GUARDRAILS
        # ==================================================

        "guardrails_validation_status": "PASSED",
    }

    # ======================================================
    # OUTPUT VALIDATION
    # ======================================================

    validation = output_validator.validate(
        output
    )

    if not validation.get("valid", False):

        return {
            "final_output": {},
            "guardrails_status": "FAILED",
            "validation_errors": validation.get(
                "errors",
                ["Output validation failed."],
            ),
            "current_step": "finalization_failed",
        }

    # ======================================================
    # SUCCESS
    # ======================================================

    return {
        "final_output": validation["validated_output"],
        "guardrails_status": "PASSED",
        "validation_errors": [],
        "current_step": "completed",
    }