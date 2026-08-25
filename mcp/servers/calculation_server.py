# mcp/servers/calculation_server.py

from typing import Any, Dict

from fastapi import FastAPI, HTTPException

app = FastAPI(title="ClaimGuard Calculation MCP Server")


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "calculation",
    }


@app.post("/tools/room_rent_deduction")
def room_rent_deduction(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    sum_insured = float(payload.get("sum_insured", 0))
    room_rent = float(payload.get("room_rent_per_day", 0))
    days = int(payload.get("days", 0))
    room_rent_cap_percent = float(
        payload.get("room_rent_cap_percent", 1)
    )

    if sum_insured <= 0:
        raise HTTPException(
            status_code=400,
            detail="sum_insured must be greater than zero.",
        )

    if room_rent <= 0 or days <= 0:
        raise HTTPException(
            status_code=400,
            detail="room rent and days must be greater than zero.",
        )

    eligible_room_rent = (
        sum_insured * room_rent_cap_percent / 100
    )

    actual_room_cost = room_rent * days
    eligible_room_cost = eligible_room_rent * days

    room_rent_deduction = max(
        0.0,
        actual_room_cost - eligible_room_cost,
    )

    return {
        "sum_insured": sum_insured,
        "room_rent_per_day": room_rent,
        "eligible_room_rent_per_day": eligible_room_rent,
        "days": days,
        "actual_room_cost": actual_room_cost,
        "eligible_room_cost": eligible_room_cost,
        "room_rent_deduction": room_rent_deduction,
    }


@app.post("/tools/proportional_deduction")
def proportional_deduction(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    actual_room_rent = float(
        payload.get("actual_room_rent", 0)
    )
    eligible_room_rent = float(
        payload.get("eligible_room_rent", 0)
    )
    associated_amount = float(
        payload.get("associated_amount", 0)
    )

    if actual_room_rent <= 0:
        raise HTTPException(
            status_code=400,
            detail="actual_room_rent must be greater than zero.",
        )

    if eligible_room_rent < 0 or associated_amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Amounts cannot be negative.",
        )

    eligible_ratio = min(
        eligible_room_rent / actual_room_rent,
        1.0,
    )

    eligible_amount = (
        associated_amount * eligible_ratio
    )

    deduction = (
        associated_amount - eligible_amount
    )

    return {
        "actual_room_rent": actual_room_rent,
        "eligible_room_rent": eligible_room_rent,
        "associated_amount": associated_amount,
        "eligible_ratio": round(eligible_ratio, 4),
        "eligible_amount": round(eligible_amount, 2),
        "proportional_deduction": round(
            deduction,
            2,
        ),
    }


@app.post("/tools/claim_balance")
def claim_balance(
    payload: Dict[str, Any],
) -> Dict[str, Any]:

    sum_insured = float(
        payload.get("sum_insured", 0)
    )
    previous_claims = float(
        payload.get("previous_claims", 0)
    )
    requested_amount = float(
        payload.get("requested_amount", 0)
    )

    if sum_insured < 0:
        raise HTTPException(
            status_code=400,
            detail="sum_insured cannot be negative.",
        )

    if previous_claims < 0 or requested_amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Claim amounts cannot be negative.",
        )

    remaining_balance = max(
        0.0,
        sum_insured - previous_claims,
    )

    maximum_approvable = min(
        requested_amount,
        remaining_balance,
    )

    return {
        "sum_insured": sum_insured,
        "previous_claims": previous_claims,
        "remaining_balance": remaining_balance,
        "requested_amount": requested_amount,
        "maximum_approvable": maximum_approvable,
    }