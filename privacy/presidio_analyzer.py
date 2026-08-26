import re
from typing import Any, Dict, List, Tuple

from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
)


class PresidioService:
    """ClaimGuard PII/PHI detection and reversible anonymization."""

    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self._register_claim_identifiers()

    def _register_claim_identifiers(self) -> None:
        """Register ClaimGuard identifiers that must be protected."""

        # --------------------------------------------------
        # UHID / Patient ID
        # --------------------------------------------------

        uhid_pattern = Pattern(
            name="uhid_pattern",
            regex=r"\bUHID[-\s]?\d{4}[-\s]?\d{4,8}\b",
            score=0.99,
        )

        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="CLAIM_PATIENT_ID",
                patterns=[uhid_pattern],
            )
        )

        # --------------------------------------------------
        # IPD / Registration Number
        # --------------------------------------------------

        ipd_pattern = Pattern(
            name="ipd_pattern",
            regex=r"\bIPD[-\s]?\d{4}[-\s]?\d{4,8}\b",
            score=0.99,
        )

        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="CLAIM_IPD_ID",
                patterns=[ipd_pattern],
            )
        )

        # --------------------------------------------------
        # Aadhaar
        # Supports:
        # 4827 1630 5941
        # 482716305941
        # --------------------------------------------------

        aadhaar_pattern = Pattern(
            name="aadhaar_pattern",
            regex=r"\b\d{4}\s?\d{4}\s?\d{4}\b",
            score=0.99,
        )

        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="IN_AADHAAR",
                patterns=[aadhaar_pattern],
            )
        )

        # --------------------------------------------------
        # PAN
        # --------------------------------------------------

        pan_pattern = Pattern(
            name="pan_pattern",
            regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
            score=0.99,
        )

        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="IN_PAN",
                patterns=[pan_pattern],
            )
        )

    def analyze(self, text: str) -> List[Any]:

        if not text.strip():
            return []

        results = self.analyzer.analyze(
            text=text,
            language="en",
        )

        allowed_entities = {
            "CLAIM_PATIENT_ID",
            "CLAIM_IPD_ID",
            "IN_AADHAAR",
            "IN_PAN",
            "PERSON",
        }

        return [
            result
            for result in results
            if result.entity_type in allowed_entities
        ]

    def anonymize(
        self,
        text: str,
    ) -> Tuple[str, Dict[str, str]]:

        if not text.strip():
            return text, {}

        results = self.analyze(text)

        if not results:
            return text, {}

        token_map: Dict[str, str] = {}
        replacements = []

        # Process right-to-left so offsets remain valid.
        sorted_results = sorted(
            results,
            key=lambda item: item.start,
            reverse=True,
        )

        token_counter = 1

        for result in sorted_results:

            original = text[
                result.start:result.end
            ]

            entity = result.entity_type

            # --------------------------------------------------
            # Clean PERSON detection
            # --------------------------------------------------

            if entity == "PERSON":
                if "\n" in original:
                    original = original.split(
                        "\n",
                        1,
                    )[0].strip()

            token = f"<{entity}_{token_counter}>"

            token_counter += 1

            token_map[token] = original

            replacements.append(
                (
                    result.start,
                    result.end,
                    token,
                )
            )

        sanitized = text

        for start, end, token in replacements:
            sanitized = (
                sanitized[:start]
                + token
                + sanitized[end:]
            )

        return sanitized, token_map


presidio_analyzer = PresidioService()