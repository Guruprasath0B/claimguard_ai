from typing import Any, Dict

from agent.state import ClaimState


def ped_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})
    patient_history = state.get("patient_history", [])

    declared_ped = str(
        claim_data.get("pre_existing_disease", "")
    ).strip()

    diagnosis = str(
        claim_data.get("diagnosis", "")
    ).strip().lower()

    # --------------------------------------------------------
    # DETERMINE WHETHER PED IS DECLARED
    # --------------------------------------------------------

    no_ped_values = {
        "",
        "no",
        "none",
        "nil",
        "not applicable",
        "n/a",
        "false",
    }

    ped_detected = (
        declared_ped.lower() not in no_ped_values
    )

    ped_condition = (
        declared_ped
        if ped_detected
        else None
    )

    # --------------------------------------------------------
    # CHECK PATIENT HISTORY
    # --------------------------------------------------------

    historical_ped = False

    for record in patient_history:

        if not isinstance(record, dict):
            continue

        content = str(
            record.get("memory")
            or record.get("text")
            or record.get("content")
            or record
        ).lower()

        if (
            "pre-existing" in content
            or "preexisting" in content
            or "ped" in content
        ):
            historical_ped = True
            break

    # --------------------------------------------------------
    # CLAIM RELATEDNESS
    # --------------------------------------------------------

    is_claim_related = False

    if ped_detected and ped_condition:
        ped_terms = [
            term.strip().lower()
            for term in ped_condition.split(",")
            if term.strip()
        ]

        is_claim_related = any(
            term in diagnosis
            for term in ped_terms
        )

    # --------------------------------------------------------
    # WAITING PERIOD
    # --------------------------------------------------------

    if not ped_detected and not historical_ped:

        waiting_period_status = "NOT_APPLICABLE"

    elif is_claim_related:

        waiting_period_status = "REQUIRES_POLICY_CHECK"

    elif historical_ped:

        waiting_period_status = "REQUIRES_POLICY_CHECK"

    else:

        waiting_period_status = "NOT_APPLICABLE"

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    assessment = {
        "ped_detected": (
            ped_detected or historical_ped
        ),
        "declared_ped": ped_condition,
        "historical_ped_detected": historical_ped,
        "is_claim_related": is_claim_related,
        "waiting_period_status": waiting_period_status,
        "diagnosis": claim_data.get(
            "diagnosis"
        ),
    }

    return {
        "ped_assessment": assessment,
        "current_step": "ped_completed",
    }