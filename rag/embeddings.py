# rag/embeddings.py

from typing import List

from langchain_openai import OpenAIEmbeddings

from config.settings import settings


class EmbeddingService:
    """Generates embeddings for ClaimGuard policy documents."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

    def embed_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        if not texts:
            return []

        return self.embeddings.embed_documents(texts)

    def embed_query(
        self,
        text: str,
    ) -> List[float]:
        if not text.strip():
            raise ValueError("Query text cannot be empty.")

        return self.embeddings.embed_query(text)


embedding_service = EmbeddingService()