# agent/nodes/clinical.py

from typing import Any, Dict

from agent.state import ClaimState
from tools.icd10 import search_diagnosis


def clinical_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})
    diagnosis = claim_data.get("diagnosis")

    if not diagnosis:
        return {
            "clinical_assessment": {
                "requires_review": True,
                "reason": "Diagnosis is missing.",
            },
            "current_step": "clinical_review_required",
        }

    try:
        icd10_results = search_diagnosis(diagnosis)

        matches = icd10_results.get("results", [])

        assessment = {
            "diagnosis": diagnosis,
            "icd10_match_found": bool(matches),
            "requires_review": not bool(matches),
            "reason": (
                "ICD-10 diagnosis verified."
                if matches
                else "No matching ICD-10 code found."
            ),
        }

        return {
            "icd10_results": icd10_results,
            "clinical_assessment": assessment,
            "current_step": "clinical_completed",
        }

    except Exception as exc:
        return {
            "clinical_assessment": {
                "requires_review": True,
                "reason": f"Clinical verification failed: {exc}",
            },
            "error": f"Clinical verification failed: {exc}",
            "current_step": "clinical_failed",
        }