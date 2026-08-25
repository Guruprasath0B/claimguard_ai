# tools/room_rent.py

from typing import Any, Dict

from mcp.client import mcp_client


def calculate_room_rent_deduction(
    sum_insured: float,
    room_rent_per_day: float,
    days: int,
    room_rent_cap_percent: float = 1.0,
) -> Dict[str, Any]:

    return mcp_client.call(
        service="calculation",
        tool="room_rent_deduction",
        arguments={
            "sum_insured": sum_insured,
            "room_rent_per_day": room_rent_per_day,
            "days": days,
            "room_rent_cap_percent": room_rent_cap_percent,
        },
    )


def calculate_proportional_deduction(
    actual_room_rent: float,
    eligible_room_rent: float,
    associated_amount: float,
) -> Dict[str, Any]:

    return mcp_client.call(
        service="calculation",
        tool="proportional_deduction",
        arguments={
            "actual_room_rent": actual_room_rent,
            "eligible_room_rent": eligible_room_rent,
            "associated_amount": associated_amount,
        },
    )