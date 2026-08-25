# ingestion/loaders.py

from pathlib import Path
from typing import List, Dict, Any
import json
import csv

from pypdf import PdfReader


class DocumentLoader:
    """Loads supported ClaimGuard input files."""

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt",
        ".json",
        ".csv",
    }

    def load(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}"
            )

        extension = path.suffix.lower()

        if extension == ".pdf":
            content = self._load_pdf(path)

        elif extension == ".txt":
            content = self._load_text(path)

        elif extension == ".json":
            content = self._load_json(path)

        elif extension == ".csv":
            content = self._load_csv(path)

        else:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return {
            "file_name": path.name,
            "file_path": str(path),
            "file_type": extension,
            "content": content,
        }

    @staticmethod
    def _load_pdf(path: Path) -> List[Dict[str, Any]]:
        reader = PdfReader(str(path))

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text() or ""

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

        return pages

    @staticmethod
    def _load_text(path: Path) -> str:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    @staticmethod
    def _load_json(path: Path) -> Any:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    @staticmethod
    def _load_csv(path: Path) -> List[Dict[str, Any]]:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)
            return list(reader)


document_loader = DocumentLoader()