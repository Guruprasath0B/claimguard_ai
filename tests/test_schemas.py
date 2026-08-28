import pytest
from pydantic import ValidationError

from schemas.claim import ClaimData, ClaimLineItem
from schemas.decision import (
    ClaimDecision,
    Deduction,
    FraudRiskAssessment,
    PEDWaitingPeriodCheck,
)
from schemas.policy import PolicyClause, PolicyContext


# ============================================================
# Claim Schema Tests
# ============================================================

def test_claim_line_item_valid():
    item = ClaimLineItem(
        code="PROC-001",
        description="Room charges",
        amount=5000.0,
    )

    assert item.code == "PROC-001"
    assert item.description == "Room charges"
    assert item.amount == 5000.0


def test_claim_line_item_rejects_negative_amount():
    with pytest.raises(ValidationError):
        ClaimLineItem(
            description="Room charges",
            amount=-100.0,
        )


def test_claim_data_valid():
    claim = ClaimData(
        claim_id="CLM-001",
        patient_identifier="PAT-001",
        policy_number="POL-001",
        diagnosis="Appendicitis",
        procedure="Appendectomy",
        sum_insured=500000.0,
        requested_amount=75000.0,
    )

    assert claim.claim_id == "CLM-001"
    assert claim.patient_identifier == "PAT-001"
    assert claim.sum_insured == 500000.0
    assert claim.requested_amount == 75000.0
    assert claim.line_items == []


def test_claim_data_rejects_negative_requested_amount():
    with pytest.raises(ValidationError):
        ClaimData(
            claim_id="CLM-001",
            patient_identifier="PAT-001",
            sum_insured=500000.0,
            requested_amount=-1000.0,
        )


def test_claim_data_default_values():
    claim = ClaimData(
        claim_id="CLM-002",
        patient_identifier="PAT-002",
        sum_insured=300000.0,
        requested_amount=25000.0,
    )

    assert claim.room_rent_cap_percent == 1.0
    assert claim.non_medical_amount == 0.0
    assert claim.line_items == []


# ============================================================
# Decision Schema Tests
# ============================================================

def test_deduction_valid():
    deduction = Deduction(
        category="Room Rent",
        amount_inr=5000.0,
        clause_reference="CLAUSE-001",
        description="Room rent exceeded policy limit",
    )

    assert deduction.category == "Room Rent"
    assert deduction.amount_inr == 5000.0


def test_fraud_risk_assessment_valid():
    assessment = FraudRiskAssessment(
        risk_level="HIGH",
        anomaly_flags=["Duplicate billing", "Unusual amount"],
    )

    assert assessment.risk_level == "HIGH"
    assert len(assessment.anomaly_flags) == 2


def test_fraud_risk_assessment_rejects_invalid_risk_level():
    with pytest.raises(ValidationError):
        FraudRiskAssessment(
            risk_level="CRITICAL",
        )


def test_ped_waiting_period_check_valid():
    ped_check = PEDWaitingPeriodCheck(
        ped_detected="Diabetes",
        is_claim_related=True,
        waiting_period_status="WAITING_PERIOD_APPLIES",
    )

    assert ped_check.ped_detected == "Diabetes"
    assert ped_check.is_claim_related is True


def test_claim_decision_valid():
    decision = ClaimDecision(
        claim_id="CLM-001",
        patient_identifier_anonymized="PAT-ANON-001",
        claim_status="PARTIAL_APPROVAL",
        requested_amount_inr=100000.0,
        approved_amount_inr=85000.0,
        ped_waiting_period_check=PEDWaitingPeriodCheck(
            ped_detected="None",
            is_claim_related=False,
            waiting_period_status="NOT_APPLICABLE",
        ),
        fraud_risk_assessment=FraudRiskAssessment(
            risk_level="LOW",
        ),
        guardrails_validation_status="PASSED",
    )

    assert decision.claim_id == "CLM-001"
    assert decision.claim_status == "PARTIAL_APPROVAL"
    assert decision.approved_amount_inr == 85000.0


def test_claim_decision_rejects_invalid_status():
    with pytest.raises(ValidationError):
        ClaimDecision(
            claim_id="CLM-001",
            patient_identifier_anonymized="PAT-ANON-001",
            claim_status="PENDING",
            requested_amount_inr=100000.0,
            approved_amount_inr=0.0,
            ped_waiting_period_check=PEDWaitingPeriodCheck(
                ped_detected="None",
                is_claim_related=False,
                waiting_period_status="NOT_APPLICABLE",
            ),
            fraud_risk_assessment=FraudRiskAssessment(
                risk_level="LOW",
            ),
            guardrails_validation_status="PASSED",
        )


# ============================================================
# Policy Schema Tests
# ============================================================

def test_policy_clause_valid():
    clause = PolicyClause(
        clause_id="CLAUSE-001",
        policy_type="INDIVIDUAL_HEALTH",
        title="Room Rent Limit",
        description="Room rent is capped at 1% of sum insured.",
        source="Policy Document",
        waiting_period_months=24,
        room_rent_cap_percent=0.01,
        applicable_categories=["Room Rent"],
    )

    assert clause.clause_id == "CLAUSE-001"
    assert clause.policy_type == "INDIVIDUAL_HEALTH"
    assert clause.waiting_period_months == 24
    assert clause.room_rent_cap_percent == 0.01


def test_policy_clause_rejects_negative_waiting_period():
    with pytest.raises(ValidationError):
        PolicyClause(
            clause_id="CLAUSE-002",
            policy_type="INDIVIDUAL_HEALTH",
            title="Waiting Period",
            description="Pre-existing disease waiting period",
            source="Policy Document",
            waiting_period_months=-12,
        )


def test_policy_context_valid():
    context = PolicyContext(
        policy_number="POL-001",
        policy_type="INDIVIDUAL_HEALTH",
        sum_insured=500000.0,
    )

    assert context.policy_number == "POL-001"
    assert context.policy_type == "INDIVIDUAL_HEALTH"
    assert context.sum_insured == 500000.0
    assert context.clauses == []


def test_policy_context_with_clause():
    clause = PolicyClause(
        clause_id="CLAUSE-001",
        policy_type="INDIVIDUAL_HEALTH",
        title="Room Rent",
        description="Room rent limitation",
        source="Policy Document",
        room_rent_cap_percent=0.01,
        applicable_categories=["Room Rent"],
    )

    context = PolicyContext(
        policy_number="POL-001",
        policy_type="INDIVIDUAL_HEALTH",
        sum_insured=500000.0,
        clauses=[clause],
    )

    assert len(context.clauses) == 1
    assert context.clauses[0].clause_id == "CLAUSE-001"