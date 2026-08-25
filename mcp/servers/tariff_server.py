# mcp/servers/tariff_server.py

from pathlib import Path
from typing import Any, Dict

import json
from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="ClaimGuard Tariff MCP Server"
)


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "tariff_master"
    / "tariffs.json"
)


def load_tariff_data() -> list:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Tariff database not found: {DATA_FILE}"
        )

    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "tariff",
    }


@app.post("/tools/get_tariff")
def get_tariff(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    procedure_code = str(
        payload.get(
            "procedure_code",
            "",
        )
    ).strip()

    hospital_id = str(
        payload.get(
            "hospital_id",
            "",
        )
    ).strip()

    if not procedure_code:
        raise HTTPException(
            status_code=400,
            detail="procedure_code is required.",
        )

    if not hospital_id:
        raise HTTPException(
            status_code=400,
            detail="hospital_id is required.",
        )

    records = load_tariff_data()

    matches = [
        record
        for record in records
        if str(
            record.get("service_code", "")
        ).strip()
        == procedure_code
        and str(
            record.get("hospital_id", "")
        ).strip()
        == hospital_id
    ]

    if not matches:
        raise HTTPException(
            status_code=404,
            detail=(
                "Tariff not found for the "
                "specified hospital and procedure."
            ),
        )

    return {
        "hospital_id": hospital_id,
        "procedure_code": procedure_code,
        "results": matches,
    }


@app.post("/tools/search_tariff")
def search_tariff(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    procedure_name = str(
        payload.get(
            "procedure_name",
            "",
        )
    ).strip().lower()

    hospital_id = str(
        payload.get(
            "hospital_id",
            "",
        )
    ).strip()

    if not procedure_name:
        raise HTTPException(
            status_code=400,
            detail="procedure_name is required.",
        )

    if not hospital_id:
        raise HTTPException(
            status_code=400,
            detail="hospital_id is required.",
        )

    records = load_tariff_data()

    matches = [
        record
        for record in records
        if procedure_name
        in str(
            record.get(
                "service_name",
                "",
            )
        ).strip().lower()
        and str(
            record.get(
                "hospital_id",
                ""
            )
        ).strip()
        == hospital_id
    ]

    if not matches:
        raise HTTPException(
            status_code=404,
            detail=(
                "Tariff not found for the "
                "specified hospital and procedure."
            ),
        )

    return {
        "hospital_id": hospital_id,
        "query": procedure_name,
        "results": matches,
    }