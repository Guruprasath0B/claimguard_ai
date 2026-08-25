from typing import Literal

from agent.state import ClaimState


def route_after_privacy(
    state: ClaimState,
) -> Literal["extraction", "error"]:
    if state.get("error"):
        return "error"

    if not state.get("sanitized_input"):
        return "error"

    return "extraction"


def route_after_extraction(
    state: ClaimState,
) -> Literal["memory", "policy", "error"]:
    if state.get("error"):
        return "error"

    claim_data = state.get("claim_data", {})

    if not claim_data:
        return "error"

    if claim_data.get("patient_identifier"):
        return "memory"

    return "policy"


def route_after_policy(
    state: ClaimState,
) -> Literal["clinical", "error"]:
    if state.get("error"):
        return "error"

    if not state.get("retrieved_policy_clauses"):
        return "error"

    return "clinical"


def route_after_clinical(
    state: ClaimState,
) -> Literal["tariff", "adjudication", "error"]:
    if state.get("error"):
        return "error"

    clinical = state.get(
        "clinical_assessment",
        {},
    )

    if clinical.get("requires_review"):
        return "adjudication"

    if not state.get("claim_data", {}).get("procedure"):
        return "adjudication"

    return "tariff"


def route_after_tariff(
    state: ClaimState,
) -> Literal["calculation", "error"]:
    if state.get("error"):
        return "error"

    if not state.get("tariff_results"):
        return "error"

    return "calculation"


def route_after_calculation(
    state: ClaimState,
) -> Literal["fraud", "error"]:
    if state.get("error"):
        return "error"

    return "fraud"


def route_after_fraud(
    state: ClaimState,
) -> Literal["adjudication", "error"]:
    if state.get("error"):
        return "error"

    return "adjudication"


def route_after_adjudication(
    state: ClaimState,
) -> Literal["finalization", "error"]:
    if state.get("error"):
        return "error"

    if not state.get("adjudication_result"):
        return "error"

    return "finalization"