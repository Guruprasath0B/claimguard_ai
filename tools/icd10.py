# tools/icd10.py

from typing import Any, Dict

from mcp.client import mcp_client


def get_icd10_code(code: str) -> Dict[str, Any]:
    return mcp_client.call(
        service="icd10",
        tool="get_code",
        arguments={
            "code": code,
        },
    )


def search_diagnosis(
    diagnosis: str,
) -> Dict[str, Any]:
    return mcp_client.call(
        service="icd10",
        tool="search_diagnosis",
        arguments={
            "diagnosis": diagnosis,
        },
    )