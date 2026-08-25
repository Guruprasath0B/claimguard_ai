# rag/chunker.py

from typing import Any, Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


class PolicyChunker:
    """Splits policy documents into retrieval-friendly chunks."""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def chunk(
        self,
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        chunks = []

        for record_index, record in enumerate(records):
            text = record.get("text", "").strip()

            if not text:
                continue

            split_texts = self.splitter.split_text(text)

            for chunk_index, chunk_text in enumerate(
                split_texts
            ):
                metadata = {
                    key: value
                    for key, value in record.items()
                    if key != "text"
                }

                metadata.update(
                    {
                        "record_index": record_index,
                        "chunk_index": chunk_index,
                        "source_type": "policy",
                    }
                )

                chunks.append(
                    {
                        "text": chunk_text,
                        "metadata": metadata,
                    }
                )

        return chunks


policy_chunker = PolicyChunker()