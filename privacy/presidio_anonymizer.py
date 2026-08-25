from typing import Any, Dict, Tuple

from privacy.presidio_analyzer import presidio_analyzer


class PresidioAnonymizer:
    """
    ClaimGuard reversible anonymization engine.

    Only explicitly approved PII/PHI entities are tokenized.
    Business identifiers, dates, claim IDs and financial amounts
    are preserved for downstream claim extraction.
    """

    # --------------------------------------------------------
    # ONLY THESE ENTITIES SHOULD BE TOKENIZED
    # --------------------------------------------------------

    ALLOWED_ENTITIES = {
        "PERSON",
        "IN_AADHAAR",
        "IN_PAN",
        "CLAIM_PATIENT_ID",
        "CLAIM_IPD_ID",
    }

    def __init__(self):
        pass

    def anonymize(
        self,
        text: str,
    ) -> Tuple[str, Dict[str, str]]:

        if not text or not text.strip():
            return text, {}

        # ----------------------------------------------------
        # RUN PRESIDIO ANALYZER
        # ----------------------------------------------------

        analyzer_results = (
            presidio_analyzer.analyze(text)
        )

        # ----------------------------------------------------
        # KEEP ONLY CLAIMGUARD APPROVED ENTITIES
        # ----------------------------------------------------

        filtered_results = [
            result
            for result in analyzer_results
            if result.entity_type
            in self.ALLOWED_ENTITIES
        ]

        if not filtered_results:
            return text, {}

        # ----------------------------------------------------
        # SORT BY POSITION
        # ----------------------------------------------------

        filtered_results = sorted(
            filtered_results,
            key=lambda result: result.start,
        )

        token_map: Dict[str, str] = {}

        replacements = []

        # ----------------------------------------------------
        # CREATE REVERSIBLE TOKENS
        # ----------------------------------------------------

        for index, result in enumerate(
            filtered_results,
            start=1,
        ):

            original_value = text[
                result.start:result.end
            ]

            token = (
                f"<{result.entity_type}_{index}>"
            )

            token_map[token] = original_value

            replacements.append(
                (
                    result.start,
                    result.end,
                    token,
                )
            )

        # ----------------------------------------------------
        # APPLY REPLACEMENTS BACKWARDS
        # ----------------------------------------------------

        anonymized_text = text

        for start, end, token in reversed(
            replacements
        ):

            anonymized_text = (
                anonymized_text[:start]
                + token
                + anonymized_text[end:]
            )

        return (
            anonymized_text,
            token_map,
        )


presidio_anonymizer = PresidioAnonymizer()