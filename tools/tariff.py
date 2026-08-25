from typing import Any, Dict

from mcp.client import mcp_client


def get_tariff(
    procedure_code: str,
    hospital_id: str,
) -> Dict[str, Any]:
    return mcp_client.call(
        service="tariff",
        tool="get_tariff",
        arguments={
            "procedure_code": procedure_code,
            "hospital_id": hospital_id,
        },
    )


def search_tariff(
    hospital_id: str,
    procedure_name: str,
) -> Dict[str, Any]:
    return mcp_client.call(
        service="tariff",
        tool="search_tariff",
        arguments={
            "hospital_id": hospital_id,
            "procedure_name": procedure_name,
        },
    )