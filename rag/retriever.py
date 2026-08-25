# rag/retriever.py

from typing import List, Optional

from langchain_core.documents import Document
from qdrant_client.http import models

from rag.qdrant import qdrant_service


class PolicyRetriever:
    """Retrieves relevant policy clauses from local Qdrant."""

    def retrieve(
        self,
        query: str,
        k: int = 5,
        source_type: Optional[str] = None,
        policy_type: Optional[str] = None,
    ) -> List[Document]:

        if not query.strip():
            return []

        query_filter = None

        conditions = []

        if source_type:
            conditions.append(
                models.FieldCondition(
                    key="metadata.source_type",
                    match=models.MatchValue(
                        value=source_type
                    ),
                )
            )

        if policy_type:
            conditions.append(
                models.FieldCondition(
                    key="metadata.policy_type",
                    match=models.MatchValue(
                        value=policy_type
                    ),
                )
            )

        if conditions:
            query_filter = models.Filter(
                must=conditions
            )

        return qdrant_service.get_store().similarity_search(
            query=query,
            k=k,
            filter=query_filter,
        )

    def retrieve_with_scores(
        self,
        query: str,
        k: int = 5,
    ):
        if not query.strip():
            return []

        return (
            qdrant_service
            .get_store()
            .similarity_search_with_score(
                query=query,
                k=k,
            )
        )


policy_retriever = PolicyRetriever()