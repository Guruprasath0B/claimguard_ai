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
# DEFAULT TEST CLAIMS
# ============================================================

DEFAULT_CLAIMS = {

    # --------------------------------------------------------
    # 1. NORMAL CLAIM
    # --------------------------------------------------------

    "1": """
Patient: Rahul Kumar
Patient ID / UHID: PAT-000001

Aadhaar: 482716305941
PAN: RAHUL4821K

Policy Number: POL-000001
Policy Type: INDIVIDUAL_HEALTH

Hospital Name: Chennai Apollo Hospital 1
Hospital ID: HSP-00001
IPD / Registration Number: IPD-2026-10001
Doctor Name: Dr. Arun Kumar

Claim ID: CLM-2026-IN-000001
Claim Type: CASHLESS_PRE_AUTH
Admission Type: Planned

Admission Date: 2026-08-20
Discharge Date: 2026-08-24

Diagnosis: Acute Appendicitis
Procedure: Laparoscopic Appendectomy

Pre-existing Disease: No

Room Rent per Day (₹): 5000
Total Bill (₹): 85000
Requested Amount (₹): 80000
Sum Insured (₹): 500000
""".strip(),

    # --------------------------------------------------------
    # 2. SAME PATIENT - MEM0 HISTORY TEST
    # --------------------------------------------------------

    "2": """
Patient: Rahul Kumar
Patient ID / UHID: PAT-000001

Aadhaar: 482716305941
PAN: RAHUL4821K

Policy Number: POL-000001
Policy Type: INDIVIDUAL_HEALTH

Hospital Name: Chennai Apollo Hospital 1
Hospital ID: HSP-00001
IPD / Registration Number: IPD-2026-10002
Doctor Name: Dr. Arun Kumar

Claim ID: CLM-2026-IN-000002
Claim Type: CASHLESS_PRE_AUTH
Admission Type: Planned

Admission Date: 2026-08-21
Discharge Date: 2026-08-25

Diagnosis: Acute Appendicitis
Procedure: Laparoscopic Appendectomy

Pre-existing Disease: No

Room Rent per Day (₹): 2500
Total Bill (₹): 60000
Requested Amount (₹): 55000
Sum Insured (₹): 500000
""".strip(),

    # --------------------------------------------------------
    # 3. DIFFERENT PATIENT
    # --------------------------------------------------------

    "3": """
Patient: Priya Sharma
Patient ID / UHID: PAT-000002

Aadhaar: 583927164205
PAN: PRIYA5832L

Policy Number: POL-000002
Policy Type: INDIVIDUAL_HEALTH

Hospital Name: Chennai Apollo Hospital 2
Hospital ID: HSP-00002
IPD / Registration Number: IPD-2026-20001
Doctor Name: Dr. Meena Sharma

Claim ID: CLM-2026-IN-000003
Claim Type: CASHLESS_PRE_AUTH
Admission Type: Emergency

Admission Date: 2026-08-22
Discharge Date: 2026-08-25

Diagnosis: Acute Appendicitis
Procedure: Laparoscopic Appendectomy

Pre-existing Disease: No

Room Rent per Day (₹): 3000
Total Bill (₹): 70000
Requested Amount (₹): 65000
Sum Insured (₹): 300000
""".strip(),

    # --------------------------------------------------------
    # 4. CLINICAL / ICD-10 REVIEW TEST
    # --------------------------------------------------------

    "4": """
Patient: Suresh Kumar
Patient ID / UHID: PAT-000003

Aadhaar: 694138275316
PAN: SURESH4932P

Policy Number: POL-000003
Policy Type: INDIVIDUAL_HEALTH

Hospital Name: Chennai Apollo Hospital 3
Hospital ID: HSP-00003
IPD / Registration Number: IPD-2026-30001
Doctor Name: Dr. Ravi Kumar

Claim ID: CLM-2026-IN-000004
Claim Type: CASHLESS_PRE_AUTH
Admission Type: Planned

Admission Date: 2026-08-20
Discharge Date: 2026-08-25

Diagnosis: Unknown Disease
Procedure: Unknown Procedure

Pre-existing Disease: No

Room Rent per Day (₹): 4000
Total Bill (₹): 90000
Requested Amount (₹): 85000
Sum Insured (₹): 500000
""".strip(),

}


# ============================================================
# CLAIM INPUT
# ============================================================

def get_claim_input():

    print("\n" + "=" * 70)
    print("CLAIMGUARD AI - CLAIM INPUT")
    print("=" * 70)

    print("\nAvailable default test claims:\n")

    print("1. Normal appendicitis claim")
    print("2. Same patient - second claim (Mem0 history test)")
    print("3. Different patient - normal claim")
    print("4. Clinical verification test")
    print("5. Enter your own claim")

    print("\n" + "-" * 70)

    choice = input(
        "\nSelect an option [1-5]: "
    ).strip()

    # --------------------------------------------------------
    # DEFAULT CLAIM
    # --------------------------------------------------------

    if choice in DEFAULT_CLAIMS:

        claim_input = DEFAULT_CLAIMS[choice]

        print("\nUsing default test claim...")
        print("-" * 70)

        print(claim_input)

        return claim_input

    # --------------------------------------------------------
    # CUSTOM USER CLAIM
    # --------------------------------------------------------

    if choice == "5":

        print("\n" + "=" * 70)
        print("ENTER CUSTOM CLAIM")
        print("=" * 70)

        print(
            "\nEnter the claim details using the following format."
        )

        print(
            "Type END on a new line when finished.\n"
        )

        print(
            "Patient Name:"
        )
        print(
            "Patient ID / UHID:"
        )
        print(
            "Aadhaar:"
        )
        print(
            "PAN:"
        )
        print(
            "Policy Number:"
        )
        print(
            "Policy Type:"
        )
        print(
            "Hospital Name:"
        )
        print(
            "Hospital ID:"
        )
        print(
            "IPD / Registration Number:"
        )
        print(
            "Doctor Name:"
        )
        print(
            "Claim ID:"
        )
        print(
            "Claim Type:"
        )
        print(
            "Admission Type:"
        )
        print(
            "Admission Date (YYYY-MM-DD):"
        )
        print(
            "Discharge Date (YYYY-MM-DD):"
        )
        print(
            "Diagnosis:"
        )
        print(
            "Procedure:"
        )
        print(
            "Pre-existing Disease:"
        )
        print(
            "Room Rent per Day (₹):"
        )
        print(
            "Total Bill (₹):"
        )
        print(
            "Requested Amount (₹):"
        )
        print(
            "Sum Insured (₹):"
        )

        print("\nNow enter your claim:\n")

        lines = []

        while True:

            line = input()

            if line.strip().upper() == "END":
                break

            lines.append(line)

        claim_input = "\n".join(
            lines
        ).strip()

        # ----------------------------------------------------
        # EMPTY CUSTOM INPUT -> DEFAULT
        # ----------------------------------------------------

        if not claim_input:

            print(
                "\nNo claim entered."
            )

            print(
                "Using default claim 1."
            )

            return DEFAULT_CLAIMS["1"]

        print("\n" + "=" * 70)
        print("CUSTOM CLAIM RECEIVED")
        print("=" * 70)

        print(claim_input)

        return claim_input

    # --------------------------------------------------------
    # INVALID OPTION -> DEFAULT
    # --------------------------------------------------------

    print(
        "\nInvalid selection."
    )

    print(
        "Using default claim 1."
    )

    return DEFAULT_CLAIMS["1"]


# ============================================================
# CLAIM PROCESSING
# ============================================================

def run_claim_guard(
    claim_input: str,
):

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

            "current_step":
                "graph_execution_failed",
        }


# ============================================================
# RESULT DISPLAY
# ============================================================

def display_claim_result(
    result,
):

    final = result.get(
        "final_output",
        {},
    )

    if not final:

        print(
            "\nClaim processing failed."
        )

        print(
            "\nDEBUG RESULT:"
        )

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

            if isinstance(
                deduction,
                dict,
            ):

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

        print(
            "Anomaly Flags         :"
        )

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

    claim_input = get_claim_input()

    print("\n" + "=" * 70)
    print("STARTING CLAIMGUARD PIPELINE")
    print("=" * 70)

    result = run_claim_guard(
        claim_input
    )

    display_claim_result(
        result
    )


if __name__ == "__main__":
    main()