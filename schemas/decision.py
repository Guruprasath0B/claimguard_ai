# schemas/decision.py

from typing import List, Literal

from pydantic import BaseModel, Field


class Deduction(BaseModel):
    category: str
    amount_inr: float = Field(ge=0)
    clause_reference: str
    description: str


class PEDWaitingPeriodCheck(BaseModel):
    ped_detected: str
    is_claim_related: bool
    waiting_period_status: str


class FraudRiskAssessment(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    anomaly_flags: List[str] = Field(
        default_factory=list
    )


class ClaimDecision(BaseModel):
    claim_id: str
    patient_identifier_anonymized: str

    claim_status: Literal[
        "APPROVED",
        "PARTIAL_APPROVAL",
        "REJECTED",
        "QUERY_RAISED",
    ]

    requested_amount_inr: float = Field(ge=0)
    approved_amount_inr: float = Field(ge=0)

    deductions: List[Deduction] = Field(
        default_factory=list
    )

    ped_waiting_period_check: PEDWaitingPeriodCheck

    fraud_risk_assessment: FraudRiskAssessment

    guardrails_validation_status: Literal[
        "PASSED",
        "FAILED",
    ]