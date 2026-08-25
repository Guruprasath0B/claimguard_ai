# agent/state.py

from typing import Any, Dict, List, Optional, TypedDict


class ClaimState(TypedDict, total=False):
    # Input
    claim_id: str
    raw_input: str
    input_files: List[str]

    # Privacy
    sanitized_input: str
    presidio_token_map: Dict[str, str]

    # Extracted claim
    claim_data: Dict[str, Any]

    # Policy RAG
    policy_query: str
    retrieved_policy_clauses: List[Dict[str, Any]]

    # Patient memory
    patient_id: str
    patient_history: List[Dict[str, Any]]

    # Clinical assessment
    icd10_results: Dict[str, Any]
    clinical_assessment: Dict[str, Any]

    # Tools / calculations
    tariff_results: Dict[str, Any]
    calculation_results: Dict[str, Any]

    # Fraud
    fraud_assessment: Dict[str, Any]

    # Adjudication
    adjudication_result: Dict[str, Any]

    # Guardrails
    validation_errors: List[str]
    guardrails_status: str

    # Final response
    final_output: Dict[str, Any]

    # Workflow control
    current_step: str
    error: Optional[str]