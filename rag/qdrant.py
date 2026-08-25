# rag/qdrant.py

from typing import Any, Dict, List

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from config.settings import settings
from rag.embeddings import embedding_service


class QdrantService:
    """Local persistent Qdrant vector-store service for ClaimGuard."""

    def __init__(self):
        settings.QDRANT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Embedded/local Qdrant.
        # No host, port, Docker, or external Qdrant server.
        self.client = QdrantClient(
            path=str(settings.QDRANT_DIR)
        )

        self.vector_store = None

    # ---------------------------------------------------------
    # Health Check
    # ---------------------------------------------------------
    def health_check(self) -> bool:
        """Check whether local Qdrant is available."""

        try:
            self.client.get_collections()
            return True

        except Exception:
            return False

    # ---------------------------------------------------------
    # Collection
    # ---------------------------------------------------------
    def _collection_exists(self) -> bool:
        """Check whether the ClaimGuard collection exists."""

        collections = (
            self.client
            .get_collections()
            .collections
        )

        return any(
            collection.name
            == settings.QDRANT_COLLECTION
            for collection in collections
        )

    def _create_collection(self) -> None:
        """Create the local Qdrant collection."""

        if self._collection_exists():
            return

        self.client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=Distance.COSINE,
            ),
        )

    # ---------------------------------------------------------
    # Get Existing Store
    # ---------------------------------------------------------
    def get_store(self) -> QdrantVectorStore:
        """Return the LangChain Qdrant vector store."""

        if self.vector_store is None:

            self._create_collection()

            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=settings.QDRANT_COLLECTION,
                embedding=embedding_service.embeddings,
            )

        return self.vector_store

    # ---------------------------------------------------------
    # Create / Index Store
    # ---------------------------------------------------------
    def create_store(
        self,
        chunks: List[Dict[str, Any]],
    ) -> QdrantVectorStore:
        """Create and populate the ClaimGuard policy collection."""

        if not chunks:
            raise ValueError(
                "No chunks provided for Qdrant."
            )

        documents = [
            Document(
                page_content=chunk["text"],
                metadata=chunk.get(
                    "metadata",
                    {},
                ),
            )
            for chunk in chunks
        ]

        # Remove the previous collection so indexing
        # always creates a clean knowledge base.
        if self._collection_exists():

            self.client.delete_collection(
                settings.QDRANT_COLLECTION
            )

            self.vector_store = None

        # Create collection explicitly.
        self._create_collection()

        # IMPORTANT:
        # Use the already-created local Qdrant client.
        # LangChain performs the embedding through
        # OpenAIEmbeddings.
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.QDRANT_COLLECTION,
            embedding=embedding_service.embeddings,
        )

        # LangChain handles document embedding + insertion.
        self.vector_store.add_documents(
            documents
        )

        print(
            f"Indexed {len(documents)} policy chunks "
            f"into local Qdrant."
        )

        return self.vector_store

    # ---------------------------------------------------------
    # Add Additional Chunks
    # ---------------------------------------------------------
    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:
        """Add additional policy chunks."""

        if not chunks:
            return

        documents = [
            Document(
                page_content=chunk["text"],
                metadata=chunk.get(
                    "metadata",
                    {},
                ),
            )
            for chunk in chunks
        ]

        self.get_store().add_documents(
            documents
        )

    # ---------------------------------------------------------
    # Similarity Search
    # ---------------------------------------------------------
    def similarity_search(
        self,
        query: str,
        k: int = 5,
    ) -> List[Document]:
        """Retrieve relevant policy documents."""

        if not query.strip():
            return []

        return self.get_store().similarity_search(
            query=query,
            k=k,
        )

    # ---------------------------------------------------------
    # Similarity Search With Scores
    # ---------------------------------------------------------
    def similarity_search_with_scores(
        self,
        query: str,
        k: int = 5,
    ):
        """Retrieve policy documents with similarity scores."""

        if not query.strip():
            return []

        return (
            self.get_store()
            .similarity_search_with_score(
                query=query,
                k=k,
            )
        )


qdrant_service = QdrantService()