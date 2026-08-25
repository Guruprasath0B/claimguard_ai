# ingestion/parsers.py

from typing import Any, Dict, List


class DocumentParser:
    """Converts loaded documents into normalized text records."""

    def parse(
        self,
        loaded_document: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        file_type = loaded_document["file_type"]
        content = loaded_document["content"]

        if file_type == ".pdf":
            return self._parse_pdf(content)

        if file_type == ".txt":
            return self._parse_text(content)

        if file_type == ".json":
            return self._parse_json(content)

        if file_type == ".csv":
            return self._parse_csv(content)

        raise ValueError(
            f"Unsupported document type: {file_type}"
        )

    @staticmethod
    def _parse_pdf(
        pages: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        records = []

        for page in pages:
            text = page.get("text", "").strip()

            if not text:
                continue

            records.append(
                {
                    "text": text,
                    "page_number": page[
                        "page_number"
                    ],
                    "record_type": "pdf_page",
                }
            )

        return records

    @staticmethod
    def _parse_text(
        text: str,
    ) -> List[Dict[str, Any]]:

        return [
            {
                "text": text.strip(),
                "record_type": "text_document",
            }
        ] if text.strip() else []

    @staticmethod
    def _parse_json(
        data: Any,
    ) -> List[Dict[str, Any]]:

        records = []

        if isinstance(data, list):

            for index, item in enumerate(data):

                records.append(
                    {
                        "text": str(item),
                        "record_number": index + 1,
                        "record_type": "json_record",
                    }
                )

        elif isinstance(data, dict):

            records.append(
                {
                    "text": str(data),
                    "record_number": 1,
                    "record_type": "json_object",
                }
            )

        return records

    @staticmethod
    def _parse_csv(
        rows: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        records = []

        for index, row in enumerate(rows):

            text = " | ".join(
                f"{key}: {value}"
                for key, value in row.items()
            )

            records.append(
                {
                    "text": text,
                    "record_number": index + 1,
                    "record_type": "csv_record",
                }
            )

        return records


document_parser = DocumentParser()