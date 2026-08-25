# agent/nodes/policy.py

from typing import Any, Dict

from agent.state import ClaimState
from rag.retriever import policy_retriever


def policy_node(state: ClaimState) -> Dict[str, Any]:
    claim_data = state.get("claim_data", {})

    query = (
        f"Policy eligibility for diagnosis "
        f"{claim_data.get('diagnosis', '')}, "
        f"procedure {claim_data.get('procedure', '')}, "
        f"room rent and claim amount rules"
    )

    try:
        documents = policy_retriever.retrieve(
            query=query,
            k=5,
            source_type="policy",
        )

        clauses = [
            {
                "text": document.page_content,
                "metadata": document.metadata,
            }
            for document in documents
        ]

        return {
            "policy_query": query,
            "retrieved_policy_clauses": clauses,
            "current_step": "policy_completed",
        }

    except Exception as exc:
        return {
            "retrieved_policy_clauses": [],
            "error": f"Policy retrieval failed: {exc}",
            "current_step": "policy_failed",
        }