from datetime import datetime
from typing import Any, Dict, List, Optional
import re


class ClaimExtractor:
    """Extracts structured claim information from normalized text."""

    def extract(
        self,
        records: List[Dict[str, Any]],
        token_map: Optional[Dict[str, str]] = None,
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
                value = value.replace(token, original)

            return value

        # ======================================================
        # DATES
        # ======================================================

        admission_date = self._extract(
            text,
            r"(?:Admission Date|Date of Admission)\s*:\s*([0-9/-]+)",
        )

        discharge_date = self._extract(
            text,
            r"(?:Discharge Date|Date of Discharge)\s*:\s*([0-9/-]+)",
        )

        admission_date = restore(admission_date)
        discharge_date = restore(discharge_date)

        hospitalization_days = (
            self._calculate_hospitalization_days(
                admission_date,
                discharge_date,
            )
        )

        # ======================================================
        # RETURN STRUCTURED CLAIM
        # ======================================================

        return {
            # --------------------------------------------------
            # CLAIM
            # --------------------------------------------------

            "claim_id": restore(
                self._extract(
                    text,
                    r"Claim ID\s*:\s*([A-Z0-9-]+)",
                )
            ),

            # --------------------------------------------------
            # PATIENT
            # --------------------------------------------------

            "patient_name": restore(
                self._extract(
                    text,
                    r"(?:Patient Name|Patient)\s*:\s*(.+?)(?:\s*\n\s*Patient ID\s*/\s*UHID:|\s*\n\s*Patient ID:|\s*\n\s*UHID:|$)",
                )
            ),

            "patient_identifier": restore(
                self._extract(
                    text,
                    r"(?:Patient ID\s*/\s*UHID|Patient ID|UHID)\s*:\s*([A-Za-z0-9-]+)",
                )
            ),

            "aadhaar": restore(
                self._extract(
                    text,
                    r"Aadhaar\s*:\s*(<IN_AADHAAR_\d+>|[0-9Xx\s-]+)",
                )
            ),

            "pan": restore(
                self._extract(
                    text,
                    r"PAN\s*:\s*(<IN_PAN_\d+>|[A-Z]{5}[0-9]{4}[A-Z])",
                )
            ),

            # --------------------------------------------------
            # POLICY
            # --------------------------------------------------

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

            # --------------------------------------------------
            # HOSPITAL
            # --------------------------------------------------

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
                    r"(?:IPD\s*/\s*Registration Number|IPD Registration Number|IPD Number|Registration Number)\s*:\s*(<CLAIM_IPD_ID_\d+>|[A-Z0-9-]+)",
                )
            ),

            "doctor_name": restore(
                self._extract(
                    text,
                    r"Doctor Name\s*:\s*(.+)",
                )
            ),

            # --------------------------------------------------
            # CLAIM TYPE / ADMISSION
            # --------------------------------------------------

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

            # --------------------------------------------------
            # DATES
            # --------------------------------------------------

            "admission_date": admission_date,

            "discharge_date": discharge_date,

            "hospitalization_days": hospitalization_days,

            # --------------------------------------------------
            # CLINICAL
            # --------------------------------------------------

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

            # --------------------------------------------------
            # FINANCIAL
            # --------------------------------------------------

            "room_rent_per_day": self._extract_amount(
                text,
                r"(?:Room Rent|Room Charges)(?:\s+per\s+Day)?(?:\s*\(₹\))?\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
            ),

            "total_bill": self._extract_amount(
                text,
                r"(?:Total Bill|Total Amount|Bill Amount)(?:\s*\(₹\))?\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
            ),

            "requested_amount": self._extract_amount(
                text,
                r"Requested Amount(?:\s*\(₹\))?\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
            ),

            "sum_insured": self._extract_amount(
                text,
                r"(?:Sum Insured|SI)(?:\s*\(₹\))?\s*:\s*₹?\s*([\d,]+(?:\.\d+)?)",
            ),
        }

    # ======================================================
    # GENERIC TEXT EXTRACTION
    # ======================================================

    @staticmethod
    def _extract(
        text: str,
        pattern: str,
    ) -> Optional[str]:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            return None

        return match.group(1).strip()

    # ======================================================
    # FINANCIAL AMOUNT EXTRACTION
    # ======================================================

    @staticmethod
    def _extract_amount(
        text: str,
        pattern: str,
    ) -> Optional[float]:

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

        except (ValueError, TypeError):
            return None

    # ======================================================
    # HOSPITALIZATION DAYS
    # ======================================================

    @staticmethod
    def _calculate_hospitalization_days(
        admission_date: Optional[str],
        discharge_date: Optional[str],
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