# memory/patient_history.py

from typing import Any, Dict, List

from memory.mem0 import mem0_service


class PatientHistoryService:
    """ClaimGuard patient history management."""

    def save_claim_history(
        self,
        patient_id: str,
        claim_data: Dict[str, Any],
    ) -> Any:

        message = {
            "role": "user",
            "content": (
                f"Patient claim history: {claim_data}"
            ),
        }

        return mem0_service.add_memory(
            user_id=patient_id,
            messages=[message],
            metadata={
                "type": "claim_history",
                "patient_id": patient_id,
                "claim_id": claim_data.get("claim_id"),
            },
        )

    def get_relevant_history(
        self,
        patient_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:

        return mem0_service.search_memory(
            user_id=patient_id,
            query=query,
            limit=limit,
        )

    def get_patient_history(
        self,
        patient_id: str,
    ) -> List[Dict[str, Any]]:

        return mem0_service.get_all_memories(
            user_id=patient_id
        )


patient_history_service = PatientHistoryService()