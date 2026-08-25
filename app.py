import json

from dotenv import load_dotenv

load_dotenv()

from agent.graph import claim_guard_graph
from guardrails.input_guard import input_guard
from rag.indexer import policy_indexer
from rag.qdrant import qdrant_service
from config.settings import settings


# ============================================================
# QDRANT INITIALIZATION
# ============================================================

def initialize_qdrant():
    """Initialize local Qdrant and index policies if required."""

    if not qdrant_service.health_check():
        raise RuntimeError(
            "Local Qdrant initialization failed."
        )

    collections = [
        collection.name
        for collection in qdrant_service.client
        .get_collections()
        .collections
    ]

    if settings.QDRANT_COLLECTION not in collections:
        print(
            "\nInitializing ClaimGuard policy knowledge base..."
        )

        result = policy_indexer.index()

        if result["status"] != "success":
            raise RuntimeError(
                result.get(
                    "message",
                    "Policy indexing failed.",
                )
            )

        print(
            f"Indexed {result['indexed_chunks']} "
            "policy chunks into Qdrant."
        )

    else:
        print(
            "\nClaimGuard policy knowledge base "
            "already exists."
        )


# ============================================================
# DEFAULT TEST CLAIM
# ============================================================

def get_default_test_claim():
    """
    Return a fixed synthetic claim for pipeline testing.

    This avoids manual input while we debug the
    ClaimGuard workflow.
    """

    return """
Patient: Rahul Kumar
Patient ID / UHID: UHID-2026-45821

Aadhaar: 1234 5678 9012
PAN: ABCDE1234F

Policy Number: POL-IND-2026-001
Policy Type: INDIVIDUAL_HEALTH

Hospital Name: Apollo City Hospital
Hospital ID: HSP-00001
IPD / Registration Number: IPD-2026-7845
Doctor Name: Dr. Arun Kumar

Claim ID: CLM-2026-AB-1001
Claim Type: Cashless
Admission Type: Planned

Admission Date: 2026-08-20
Discharge Date: 2026-08-24

Diagnosis: Acute appendicitis
Procedure: Laparoscopic appendectomy

Pre-existing Disease: No

Room Rent: ₹5000
Total Bill: ₹85000
Requested Amount: ₹80000
Sum Insured: ₹500000
""".strip()


# ============================================================
# CLAIM PROCESSING
# ============================================================

def run_claim_guard(claim_input: str):
    """Run the ClaimGuard LangGraph pipeline."""

    input_validation = input_guard.validate(
        claim_input
    )

    if not input_validation["valid"]:
        return {
            "guardrails_status": "FAILED",
            "validation_errors": input_validation.get(
                "errors",
                [],
            ),
            "final_output": {},
        }

    initial_state = {
        "raw_input": claim_input,
        "claim_data": {},
        "patient_history": [],
        "retrieved_policy_clauses": [],
        "icd10_results": {},
        "clinical_assessment": {},
        "tariff_results": {},
        "calculation_results": {},
        "fraud_assessment": {},
        "adjudication_result": {},
        "final_output": {},
        "validation_errors": [],
        "guardrails_status": "PENDING",
        "current_step": "starting",
        "error": None,
    }

    try:
        return claim_guard_graph.invoke(
            initial_state
        )

    except Exception as exc:
        return {
            "guardrails_status": "FAILED",
            "validation_errors": [
                f"Claim processing failed: {exc}"
            ],
            "final_output": {},
            "error": str(exc),
            "current_step": "graph_execution_failed",
        }


# ============================================================
# RESULT DISPLAY
# ============================================================

def display_claim_result(result):
    """Display the final claim decision."""

    final = result.get(
        "final_output",
        {},
    )

    if not final:
        print("\nClaim processing failed.")

        print("\nDEBUG RESULT:")
        print(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )
        return

    print("\n" + "=" * 70)
    print("CLAIMGUARD AI - CLAIM DECISION")
    print("=" * 70)

    print(
        f"\nClaim ID              : "
        f"{final.get('claim_id', 'N/A')}"
    )

    print(
        f"Claim Status          : "
        f"{final.get('claim_status', 'N/A')}"
    )

    print(
        f"Requested Amount      : ₹"
        f"{float(final.get('requested_amount_inr', 0)):,.2f}"
    )

    print(
        f"Approved Amount       : ₹"
        f"{float(final.get('approved_amount_inr', 0)):,.2f}"
    )

    # --------------------------------------------------------
    # DEDUCTIONS
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("DEDUCTIONS")
    print("-" * 70)

    deductions = final.get(
        "deductions",
        [],
    )

    total_deduction = 0.0

    if deductions:

        for deduction in deductions:

            if isinstance(deduction, dict):

                description = deduction.get(
                    "description",
                    deduction.get(
                        "type",
                        "Deduction",
                    ),
                )

                amount = float(
                    deduction.get(
                        "amount_inr",
                        deduction.get(
                            "amount",
                            0,
                        ),
                    )
                )

                total_deduction += amount

                print(
                    f"{description:<30} : "
                    f"₹{amount:,.2f}"
                )

            else:
                print(
                    f"- {deduction}"
                )

    else:

        requested = float(
            final.get(
                "requested_amount_inr",
                0,
            )
        )

        approved = float(
            final.get(
                "approved_amount_inr",
                0,
            )
        )

        total_deduction = max(
            0.0,
            requested - approved,
        )

        print(
            f"Room Rent Deduction         : "
            f"₹{total_deduction:,.2f}"
        )

    print(
        f"Total Deduction             : "
        f"₹{total_deduction:,.2f}"
    )

    # --------------------------------------------------------
    # FRAUD
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("FRAUD RISK ASSESSMENT")
    print("-" * 70)

    fraud = final.get(
        "fraud_risk_assessment",
        {},
    )

    print(
        f"Risk Level            : "
        f"{fraud.get('risk_level', 'N/A')}"
    )

    anomaly_flags = fraud.get(
        "anomaly_flags",
        [],
    )

    if anomaly_flags:

        print("Anomaly Flags         :")

        for flag in anomaly_flags:
            print(
                f"  - {flag}"
            )

    else:

        print(
            "Anomaly Flags         : None"
        )

    # --------------------------------------------------------
    # PED
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("PED / WAITING PERIOD CHECK")
    print("-" * 70)

    ped = final.get(
        "ped_waiting_period_check",
        {},
    )

    print(
        f"PED Detected          : "
        f"{ped.get('ped_detected', 'N/A')}"
    )

    print(
        f"Claim Related         : "
        f"{ped.get('is_claim_related', 'N/A')}"
    )

    print(
        f"Waiting Period        : "
        f"{ped.get('waiting_period_status', 'N/A')}"
    )

    # --------------------------------------------------------
    # GUARDRAILS
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("GUARDRAILS")
    print("-" * 70)

    print(
        f"Validation Status     : "
        f"{final.get('guardrails_validation_status', 'N/A')}"
    )

    # --------------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL CLAIM DECISION")
    print("=" * 70)

    status = final.get(
        "claim_status",
        "UNKNOWN",
    )

    print(
        f"\n>>> {status} <<<"
    )

    print("\n" + "=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "CLAIMGUARD AI - ENTERPRISE CLAIM RESOLUTION AGENT"
    )
    print("=" * 70)

    try:

        initialize_qdrant()

    except Exception as exc:

        print(
            "\nQdrant initialization failed."
        )

        print(
            f"Error: {exc}"
        )

        return

    # --------------------------------------------------------
    # USE DEFAULT TEST CLAIM
    # --------------------------------------------------------

    claim_input = get_default_test_claim()

    print("\nUsing default test claim...")
    print("-" * 70)

    print(claim_input)

    # --------------------------------------------------------
    # RUN PIPELINE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("STARTING CLAIMGUARD PIPELINE")
    print("=" * 70)

    result = run_claim_guard(
        claim_input
    )

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    display_claim_result(
        result
    )


if __name__ == "__main__":
    main()