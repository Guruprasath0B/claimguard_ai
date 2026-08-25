# mcp/servers/icd10_server.py

from pathlib import Path
from typing import Any, Dict
import json

from fastapi import FastAPI, HTTPException

app = FastAPI(title="ClaimGuard ICD-10 MCP Server")

DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "synthetic"
    / "icd10_data.json"
)


def load_icd10_data() -> list:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"ICD-10 database not found: {DATA_FILE}"
        )

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "icd10",
    }


@app.post("/tools/get_code")
def get_code(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    code = payload.get("code")

    if not code:
        raise HTTPException(
            status_code=400,
            detail="code is required.",
        )

    records = load_icd10_data()

    matches = [
        record
        for record in records
        if str(record.get("code")).upper()
        == str(code).upper()
    ]

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="ICD-10 code not found.",
        )

    return {
        "code": code,
        "results": matches,
    }


@app.post("/tools/search_diagnosis")
def search_diagnosis(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    diagnosis = str(
        payload.get("diagnosis", "")
    ).strip().lower()

    if not diagnosis:
        raise HTTPException(
            status_code=400,
            detail="diagnosis is required.",
        )

    records = load_icd10_data()

    matches = [
        record
        for record in records
        if diagnosis in str(
            record.get("description", "")
        ).lower()
    ]

    return {
        "query": diagnosis,
        "results": matches,
    }