# privacy/presidio_rehydrator.py

from typing import Dict


class PresidioRehydrator:
    """
    Restores anonymized PII/PHI tokens using the
    session-specific token map.
    """

    def rehydrate(
        self,
        text: str,
        token_map: Dict[str, str],
    ) -> str:
        """
        Replace anonymization tokens with original values.

        Args:
            text: Anonymized text.
            token_map: Token -> original value mapping.

        Returns:
            Rehydrated text.
        """

        if not text or not token_map:
            return text

        rehydrated_text = text

        for token, original_value in token_map.items():
            rehydrated_text = rehydrated_text.replace(
                token,
                original_value,
            )

        return rehydrated_text


presidio_rehydrator = PresidioRehydrator()