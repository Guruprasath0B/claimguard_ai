# rag/indexer.py

import json
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.documents import Document

from config.settings import settings
from rag.qdrant import qdrant_service


class PolicyIndexer:
    """Indexes ClaimGuard policy data into local Qdrant."""

    def __init__(self):
        self.policy_dir = (
            settings.BASE_DIR / "data" / "policies"
        )

    def _load_json(
        self,
        filename: str,
    ) -> Any:
        file_path = self.policy_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Policy file not found: {file_path}"
            )

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _extract_records(
        self,
        data: Any,
    ) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            return [
                item
                for item in data
                if isinstance(item, dict)
            ]

        if isinstance(data, dict):
            for key in (
                "policies",
                "clauses",
                "documents",
                "data",
                "records",
                "items",
            ):
                value = data.get(key)

                if isinstance(value, list):
                    return [
                        item
                        for item in value
                        if isinstance(item, dict)
                    ]

        return []

    def load_policy_chunks(
        self,
    ) -> List[Dict[str, Any]]:
        chunks = []

        sources = [
            "policy_clauses.json",
            "policy_documents.json",
        ]

        for filename in sources:
            data = self._load_json(filename)
            records = self._extract_records(data)

            for index, record in enumerate(records):

                text = (
                    record.get("text")
                    or record.get("content")
                    or record.get("clause_text")
                    or record.get("description")
                    or record.get("policy_text")
                    or ""
                )

                if not isinstance(text, str):
                    text = str(text)

                text = text.strip()

                if not text:
                    continue

                metadata = {
                    "source_type": "policy",
                    "source_file": filename,
                    "policy_id": record.get(
                        "policy_id"
                    ),
                    "policy_type": record.get(
                        "policy_type"
                    ),
                    "clause_id": record.get(
                        "clause_id"
                    ),
                    "category": record.get(
                        "category"
                    ),
                }

                metadata = {
                    key: value
                    for key, value in metadata.items()
                    if value is not None
                }

                chunks.append(
                    {
                        "text": text,
                        "metadata": metadata,
                        "chunk_id": (
                            f"{filename}_{index}"
                        ),
                    }
                )

        return chunks

    def index(self) -> Dict[str, Any]:
        chunks = self.load_policy_chunks()

        if not chunks:
            return {
                "status": "failed",
                "indexed_chunks": 0,
                "message": (
                    "No usable policy records "
                    "were found."
                ),
            }

        qdrant_service.create_store(
            chunks
        )

        return {
            "status": "success",
            "indexed_chunks": len(chunks),
            "collection": (
                settings.QDRANT_COLLECTION
            ),
        }


policy_indexer = PolicyIndexer()