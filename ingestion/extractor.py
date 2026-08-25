from datetime import datetime
from typing import Any, Dict, List
import re


class ClaimExtractor:
    """Extracts structured claim information from normalized text."""

    def extract(
        self,
        records: List[Dict[str, Any]],
        token_map: Dict[str, str] | None = None,
    ) -> Dict[str, Any]:

        text = "\n".join(
            record.get("text", "")
            for record in records
        )

        token_map = token_map or {}

        def restore(value):
            if value is None:
                return None

            value = value.strip()

            for token, original in token_map.items():
                value = value.replace(
                    token,
                    original,
                )

            return value

        admission_date = self._extract(
            text,
            r"(?:Admission Date|Date of Admission)\s*:\s*([0-9/-]+)",
        )

        discharge_date = self._extract(
            text,
            r"(?:Discharge Date|Date of Discharge)\s*:\s*([0-9/-]+)",
        )

        hospitalization_days = (
            self._calculate_hospitalization_days(
                restore(admission_date),
                restore(discharge_date),
            )
        )

        return {
            "claim_id": restore(
                self._extract(
                    text,
                    r"Claim ID\s*:\s*(CLM[-\s]?\d{4}[-\s]?[A-Z]{2}[-\s]?\d+)",
                )
            ),

            "patient_name": restore(
                self._extract(
                    text,
                    r"(?:Patient Name|Patient)\s*:\s*([A-Za-z .]+)",
                )
            ),

            "patient_identifier": restore(
                self._extract(
                    text,
                    r"(?:Patient ID / UHID|Patient ID|UHID)\s*:\s*([A-Za-z0-9-]+)",
                )
            ),

            "aadhaar": restore(
                self._extract(
                    text,
                    r"Aadhaar\s*:\s*([0-9Xx\s-]+)",
                )
            ),

            "pan": restore(
                self._extract(
                    text,
                    r"PAN\s*:\s*([A-Z]{5}[0-9]{4}[A-Z])",
                )
            ),

            "policy_number": restore(
                self._extract(
                    text,
                    r"(?:Policy Number|Policy No)\s*:\s*([A-Z0-9-]+)",
                )
            ),

            "policy_type": restore(
                self._extract(
                    text,
                    r"Policy Type\s*:\s*([A-Za-z0-9_-]+)",
                )
            ),

            "hospital_name": restore(
                self._extract(
                    text,
                    r"Hospital Name\s*:\s*(.+)",
                )
            ),

            "hospital_id": restore(
                self._extract(
                    text,
                    r"Hospital ID\s*:\s*([A-Z0-9-]+)",
                )
            ),

            "ipd_registration_number": restore(
                self._extract(
                    text,
                    r"(?:IPD / Registration Number|IPD Registration Number|IPD Number|Registration Number)\s*:\s*([A-Z0-9-]+)",
                )
            ),

            "doctor_name": restore(
                self._extract(
                    text,
                    r"Doctor Name\s*:\s*(.+)",
                )
            ),

            "claim_type": restore(
                self._extract(
                    text,
                    r"Claim Type\s*:\s*(.+)",
                )
            ),

            "admission_type": restore(
                self._extract(
                    text,
                    r"Admission Type\s*:\s*(.+)",
                )
            ),

            "admission_date": restore(
                admission_date
            ),

            "discharge_date": restore(
                discharge_date
            ),

            "hospitalization_days":
                hospitalization_days,

            "diagnosis": restore(
                self._extract(
                    text,
                    r"(?:Diagnosis|Provisional Diagnosis)\s*:\s*(.+)",
                )
            ),

            "procedure": restore(
                self._extract(
                    text,
                    r"Procedure\s*:\s*(.+)",
                )
            ),

            "pre_existing_disease": restore(
                self._extract(
                    text,
                    r"Pre-existing Disease\s*:\s*(.+)",
                )
            ),

            "room_rent_per_day":
                self._extract_amount(
                    text,
                    r"(?:Room Rent|Room Charges)(?: per Day)?\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
                ),

            "total_bill":
                self._extract_amount(
                    text,
                    r"(?:Total Bill|Total Amount|Bill Amount)\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
                ),

            "requested_amount":
                self._extract_amount(
                    text,
                    r"Requested Amount\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
                ),

            "sum_insured":
                self._extract_amount(
                    text,
                    r"(?:Sum Insured|SI)\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
                ),
        }

    @staticmethod
    def _extract(
        text: str,
        pattern: str,
    ) -> str | None:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            return None

        return match.group(1).strip()

    @staticmethod
    def _extract_amount(
        text: str,
        pattern: str,
    ) -> float | None:

        value = ClaimExtractor._extract(
            text,
            pattern,
        )

        if value is None:
            return None

        try:
            return float(
                value.replace(",", "")
            )
        except ValueError:
            return None

    @staticmethod
    def _calculate_hospitalization_days(
        admission_date: str | None,
        discharge_date: str | None,
    ) -> int:

        if not admission_date or not discharge_date:
            return 1

        try:
            admission = datetime.strptime(
                admission_date,
                "%Y-%m-%d",
            )

            discharge = datetime.strptime(
                discharge_date,
                "%Y-%m-%d",
            )

            return max(
                (discharge - admission).days + 1,
                1,
            )

        except ValueError:
            return 1


claim_extractor = ClaimExtractor()