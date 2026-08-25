# memory/mem0.py

from typing import Any, Dict, List, Optional

from mem0 import Memory

from config.settings import settings


class Mem0Service:
    """Local Mem0 long-term patient memory service."""

    def __init__(self):
        self.memory = Memory()

    def add_memory(
        self,
        user_id: str,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if not user_id:
            raise ValueError("user_id is required.")

        if not messages:
            return None

        return self.memory.add(
            messages,
            user_id=user_id,
            metadata=metadata or {},
        )

    def search_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        if not user_id:
            raise ValueError("user_id is required.")

        if not query.strip():
            return []

        result = self.memory.search(
            query,
            user_id=user_id,
            limit=limit,
        )

        if isinstance(result, dict):
            return result.get("results", [])

        return result

    def get_all_memories(
        self,
        user_id: str,
    ) -> List[Dict[str, Any]]:
        if not user_id:
            raise ValueError("user_id is required.")

        result = self.memory.get_all(
            user_id=user_id
        )

        if isinstance(result, dict):
            return result.get("results", [])

        return result


mem0_service = Mem0Service()