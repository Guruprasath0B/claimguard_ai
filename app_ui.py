# app_ui.py

import streamlit as st

from app import (
    DEFAULT_CLAIMS,
    initialize_qdrant,
    run_claim_guard,
)

from utils.mcp_manager import start_mcp_servers


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ClaimGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .decision-box {
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #d1d5db;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "qdrant_initialized" not in st.session_state:
    st.session_state.qdrant_initialized = False

if "mcp_initialized" not in st.session_state:
    st.session_state.mcp_initialized = False


# ============================================================
# MCP INITIALIZATION
# ============================================================

def initialize_mcp():

    if st.session_state.mcp_initialized:
        return True

    try:

        with st.spinner(
            "Starting ClaimGuard MCP services..."
        ):

            start_mcp_servers()

        st.session_state.mcp_initialized = True

        return True

    except Exception as exc:

        st.error(
            "MCP server initialization failed."
        )

        st.exception(exc)

        return False


# ============================================================
# QDRANT INITIALIZATION
# ============================================================

def initialize_application():

    if st.session_state.qdrant_initialized:
        return True

    try:

        with st.spinner(
            "Initializing ClaimGuard policy knowledge base..."
        ):

            initialize_qdrant()

        st.session_state.qdrant_initialized = True

        return True

    except Exception as exc:

        st.error(
            "Qdrant initialization failed."
        )

        st.exception(exc)

        return False


# ============================================================
# START MCP SERVERS
# ============================================================

if not initialize_mcp():

    st.stop()


# ============================================================
# INITIALIZE QDRANT
# ============================================================

if not initialize_application():

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🛡️ ClaimGuard AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Autonomous Cashless Mediclaim Pre-Auth & TPA Fraud Detection Agent
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Claim Processing")

    st.markdown(
        """
        ClaimGuard AI evaluates healthcare insurance claims using:

        - 🔐 PII/PHI protection
        - 🧠 Patient memory
        - 📚 Policy RAG
        - 🩺 Clinical validation
        - 💰 Tariff calculation
        - 🚨 Fraud detection
        - ⚖️ Claim adjudication
        - 🛡️ Guardrails
        """
    )

    st.divider()

    st.subheader("System Status")

    st.success("MCP Services: Ready")

    st.success("Qdrant: Ready")

    st.caption("Environment: development")

    st.caption("LLM: gpt-4o-mini")

    st.caption(
        "Embedding: text-embedding-3-small"
    )


# ============================================================
# CLAIM INPUT
# ============================================================

st.header("📋 Claim Input")

input_mode = st.radio(
    "Choose claim input method",
    [
        "Default Test Claim",
        "Custom Claim",
    ],
    horizontal=True,
)


# ============================================================
# DEFAULT TEST CLAIM
# ============================================================

if input_mode == "Default Test Claim":

    claim_options = {
        "1 - Normal appendicitis claim": "1",
        "2 - Same patient / Mem0 history test": "2",
        "3 - Different patient claim": "3",
        "4 - Clinical verification test": "4",
    }

    selected_claim = st.selectbox(
        "Select a test claim",
        list(claim_options.keys()),
    )

    claim_key = claim_options[
        selected_claim
    ]

    claim_input = DEFAULT_CLAIMS[
        claim_key
    ]

    with st.expander(
        "👁️ Preview Claim Input",
        expanded=True,
    ):

        st.text_area(
            "Claim data",
            value=claim_input,
            height=350,
            disabled=True,
        )


# ============================================================
# CUSTOM CLAIM
# ============================================================

else:

    st.info(
        "Enter the claim using the field-based format "
        "expected by the ClaimGuard extraction pipeline."
    )

    default_template = """
Patient Name:
Patient ID / UHID:

Aadhaar:
PAN:

Policy Number:
Policy Type:

Hospital Name:
Hospital ID:
IPD / Registration Number:
Doctor Name:

Claim ID:
Claim Type:
Admission Type:

Admission Date (YYYY-MM-DD):
Discharge Date (YYYY-MM-DD):

Diagnosis:
Procedure:

Pre-existing Disease:

Room Rent per Day (₹):
Total Bill (₹):
Requested Amount (₹):
Sum Insured (₹):
""".strip()

    claim_input = st.text_area(
        "Claim Details",
        value=default_template,
        height=500,
        placeholder="Enter claim details here...",
    )


# ============================================================
# PROCESS CLAIM
# ============================================================

st.divider()

process_claim = st.button(
    "🚀 Analyze Claim",
    type="primary",
    use_container_width=True,
)


if process_claim:

    if not claim_input.strip():

        st.error(
            "Please provide claim information."
        )

    else:

        with st.spinner(
            "ClaimGuard AI is analyzing the claim..."
        ):

            result = run_claim_guard(
                claim_input
            )

        st.session_state.result = result

        if result.get("final_output"):

            st.success(
                "Claim processing completed successfully."
            )

        else:

            st.warning(
                "Claim processing completed, "
                "but no final decision was returned."
            )


# ============================================================
# RESULTS
# ============================================================

result = st.session_state.result


if result is not None:

    st.divider()

    st.header("📊 Claim Decision")

    final = result.get(
        "final_output",
        {},
    )


    # ========================================================
    # PROCESSING FAILURE
    # ========================================================

    if not final:

        st.error(
            "Claim processing failed."
        )

        errors = result.get(
            "validation_errors",
            [],
        )

        if errors:

            st.subheader(
                "Validation / Processing Errors"
            )

            for error in errors:

                st.error(
                    str(error)
                )

        with st.expander(
            "🔧 Debug Result"
        ):

            st.json(
                result
            )


    else:

        # ====================================================
        # BASIC CLAIM INFORMATION
        # ====================================================

        claim_id = final.get(
            "claim_id",
            "N/A",
        )

        claim_status = final.get(
            "claim_status",
            "N/A",
        )

        requested_amount = float(
            final.get(
                "requested_amount_inr",
                0,
            )
        )

        approved_amount = float(
            final.get(
                "approved_amount_inr",
                0,
            )
        )


        # ====================================================
        # TOP METRICS
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Claim ID",
                claim_id,
            )

        with col2:

            st.metric(
                "Claim Status",
                claim_status,
            )

        with col3:

            st.metric(
                "Requested Amount",
                f"₹{requested_amount:,.2f}",
            )

        with col4:

            st.metric(
                "Approved Amount",
                f"₹{approved_amount:,.2f}",
            )


        # ====================================================
        # FINAL DECISION
        # ====================================================

        st.markdown(
            f"""
            <div class="decision-box">

            <h2>Final Decision</h2>

            <h1>{claim_status}</h1>

            <p>
            Requested Amount:
            <strong>₹{requested_amount:,.2f}</strong>
            </p>

            <p>
            Approved Amount:
            <strong>₹{approved_amount:,.2f}</strong>
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )


        # ====================================================
        # DEDUCTIONS
        # ====================================================

        st.subheader(
            "💰 Deductions"
        )

        deductions = final.get(
            "deductions",
            [],
        )

        total_deduction = 0.0

        if deductions:

            deduction_rows = []

            for deduction in deductions:

                if isinstance(
                    deduction,
                    dict,
                ):

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

                    deduction_rows.append(
                        {
                            "Category": deduction.get(
                                "category",
                                "N/A",
                            ),
                            "Description": deduction.get(
                                "description",
                                "N/A",
                            ),
                            "Amount": (
                                f"₹{amount:,.2f}"
                            ),
                            "Clause": deduction.get(
                                "clause_reference",
                                "N/A",
                            ),
                        }
                    )

            if deduction_rows:

                st.dataframe(
                    deduction_rows,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No deductions were recorded."
                )

        else:

            total_deduction = max(
                0.0,
                requested_amount
                - approved_amount,
            )

            if total_deduction > 0:

                st.write(
                    f"Total deduction: "
                    f"₹{total_deduction:,.2f}"
                )

            else:

                st.success(
                    "No deductions."
                )


        # ====================================================
        # AMOUNT SUMMARY
        # ====================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Requested",
                f"₹{requested_amount:,.2f}",
            )

        with col2:

            st.metric(
                "Total Deduction",
                f"₹{total_deduction:,.2f}",
            )

        with col3:

            st.metric(
                "Approved",
                f"₹{approved_amount:,.2f}",
            )


        # ====================================================
        # FRAUD RISK
        # ====================================================

        st.subheader(
            "🚨 Fraud Risk Assessment"
        )

        fraud = final.get(
            "fraud_risk_assessment",
            {},
        )

        risk_level = fraud.get(
            "risk_level",
            "N/A",
        )

        anomaly_flags = fraud.get(
            "anomaly_flags",
            [],
        )

        fraud_col1, fraud_col2 = st.columns(2)

        with fraud_col1:

            st.metric(
                "Risk Level",
                risk_level,
            )

        with fraud_col2:

            st.metric(
                "Anomaly Count",
                len(anomaly_flags),
            )

        if anomaly_flags:

            st.warning(
                "Anomalies detected"
            )

            for flag in anomaly_flags:

                st.write(
                    f"• {flag}"
                )

        else:

            st.success(
                "No anomaly flags detected."
            )


        # ====================================================
        # PED / WAITING PERIOD
        # ====================================================

        st.subheader(
            "🩺 PED / Waiting Period Check"
        )

        ped = final.get(
            "ped_waiting_period_check",
            {},
        )

        ped_col1, ped_col2, ped_col3 = st.columns(3)

        with ped_col1:

            st.metric(
                "PED Detected",
                str(
                    ped.get(
                        "ped_detected",
                        "N/A",
                    )
                ),
            )

        with ped_col2:

            st.metric(
                "Claim Related",
                str(
                    ped.get(
                        "is_claim_related",
                        "N/A",
                    )
                ),
            )

        with ped_col3:

            st.metric(
                "Waiting Period",
                str(
                    ped.get(
                        "waiting_period_status",
                        "N/A",
                    )
                ),
            )


        # ====================================================
        # GUARDRAILS
        # ====================================================

        st.subheader(
            "🛡️ Guardrails"
        )

        guardrail_status = final.get(
            "guardrails_validation_status",
            "N/A",
        )

        if guardrail_status == "PASSED":

            st.success(
                "Guardrails validation PASSED"
            )

        elif guardrail_status == "FAILED":

            st.error(
                "Guardrails validation FAILED"
            )

        else:

            st.warning(
                f"Guardrails status: "
                f"{guardrail_status}"
            )


        # ====================================================
        # CLAIM DATA
        # ====================================================

        with st.expander(
            "👤 Extracted Claim Information"
        ):

            claim_data = result.get(
                "claim_data",
                {},
            )

            if claim_data:

                st.json(
                    claim_data
                )

            else:

                st.info(
                    "Structured claim data "
                    "is not available."
                )


        # ====================================================
        # PATIENT HISTORY
        # ====================================================

        with st.expander(
            "🧠 Patient History"
        ):

            patient_history = result.get(
                "patient_history",
                [],
            )

            if patient_history:

                st.json(
                    patient_history
                )

            else:

                st.info(
                    "No patient history returned."
                )


        # ====================================================
        # POLICY CLAUSES
        # ====================================================

        with st.expander(
            "📚 Retrieved Policy Clauses"
        ):

            policy_clauses = result.get(
                "retrieved_policy_clauses",
                [],
            )

            if policy_clauses:

                st.json(
                    policy_clauses
                )

            else:

                st.info(
                    "No policy clauses returned."
                )


        # ====================================================
        # CLINICAL ASSESSMENT
        # ====================================================

        with st.expander(
            "🩺 Clinical Assessment"
        ):

            clinical = result.get(
                "clinical_assessment",
                {},
            )

            icd10 = result.get(
                "icd10_results",
                {},
            )

            if icd10:

                st.write(
                    "**ICD-10 Results**"
                )

                st.json(
                    icd10
                )

            if clinical:

                st.write(
                    "**Clinical Assessment**"
                )

                st.json(
                    clinical
                )

            if not clinical and not icd10:

                st.info(
                    "No clinical assessment returned."
                )


        # ====================================================
        # TARIFF / CALCULATION
        # ====================================================

        with st.expander(
            "💵 Tariff & Calculation"
        ):

            tariff = result.get(
                "tariff_results",
                {},
            )

            calculation = result.get(
                "calculation_results",
                {},
            )

            if tariff:

                st.write(
                    "**Tariff Results**"
                )

                st.json(
                    tariff
                )

            if calculation:

                st.write(
                    "**Calculation Results**"
                )

                st.json(
                    calculation
                )

            if not tariff and not calculation:

                st.info(
                    "No tariff or calculation "
                    "details returned."
                )


        # ====================================================
        # ADJUDICATION
        # ====================================================

        with st.expander(
            "⚖️ Adjudication Result"
        ):

            adjudication = result.get(
                "adjudication_result",
                {},
            )

            if adjudication:

                st.json(
                    adjudication
                )

            else:

                st.info(
                    "No adjudication details returned."
                )


        # ====================================================
        # WORKFLOW STATUS
        # ====================================================

        with st.expander(
            "🔄 Workflow / Processing Status"
        ):

            current_step = result.get(
                "current_step",
                "N/A",
            )

            workflow_error = result.get(
                "error",
                None,
            )

            st.write(
                f"**Current Step:** "
                f"{current_step}"
            )

            st.write(
                f"**Guardrails Status:** "
                f"{result.get('guardrails_status', 'N/A')}"
            )

            if workflow_error:

                st.error(
                    str(workflow_error)
                )


        # ====================================================
        # RAW FINAL OUTPUT
        # ====================================================

        with st.expander(
            "🔍 Raw Final Output"
        ):

            st.json(
                final
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ClaimGuard AI | Autonomous Mediclaim "
    "Pre-Authorization and TPA Fraud Detection Agent"
)