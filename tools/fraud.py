# tools/fraud.py

from typing import Any, Dict, List


def detect_fraud_anomalies(
    claim_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Detects basic deterministic claim anomalies.
    """

    flags: List[Dict[str, Any]] = []

    admission_date = claim_data.get("admission_date")
    discharge_date = claim_data.get("discharge_date")
    total_bill = claim_data.get("total_bill")
    line_items = claim_data.get("line_items", [])

    # Timeline check
    if admission_date and discharge_date:
        if discharge_date < admission_date:
            flags.append(
                {
                    "type": "TIMELINE_MISMATCH",
                    "severity": "HIGH",
                    "description": (
                        "Discharge date occurs before admission date."
                    ),
                }
            )

    # Duplicate / suspicious billing check
    seen_items = set()

    for item in line_items:
        item_code = item.get("code")

        if item_code and item_code in seen_items:
            flags.append(
                {
                    "type": "DUPLICATE_BILLING",
                    "severity": "MEDIUM",
                    "description": (
                        f"Duplicate billing detected for {item_code}."
                    ),
                }
            )

        if item_code:
            seen_items.add(item_code)

    # Excessive non-medical items
    non_medical_amount = float(
        claim_data.get(
            "non_medical_amount",
            0,
        )
    )

    if total_bill and non_medical_amount > 0:
        ratio = non_medical_amount / float(total_bill)

        if ratio > 0.20:
            flags.append(
                {
                    "type": "HIGH_NON_MEDICAL_BILLING",
                    "severity": "MEDIUM",
                    "description": (
                        "Non-medical charges exceed 20% "
                        "of the total bill."
                    ),
                }
            )

    # Risk calculation
    severity_weights = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    risk_score = sum(
        severity_weights.get(
            flag["severity"],
            0,
        )
        for flag in flags
    )

    if risk_score >= 5:
        risk_level = "HIGH"
    elif risk_score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "anomaly_flags": flags,
    }