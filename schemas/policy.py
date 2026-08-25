# schemas/policy.py

from typing import List, Optional

from pydantic import BaseModel, Field


class PolicyClause(BaseModel):
    clause_id: str
    policy_type: str
    title: str
    description: str
    source: str

    waiting_period_months: Optional[int] = Field(
        default=None,
        ge=0,
    )

    room_rent_cap_percent: Optional[float] = Field(
        default=None,
        ge=0,
    )

    applicable_categories: List[str] = Field(
        default_factory=list
    )


class PolicyContext(BaseModel):
    policy_number: Optional[str] = None
    policy_type: str
    sum_insured: float = Field(ge=0)

    room_rent_cap_percent: Optional[float] = Field(
        default=None,
        ge=0,
    )

    waiting_period_months: Optional[int] = Field(
        default=None,
        ge=0,
    )

    clauses: List[PolicyClause] = Field(
        default_factory=list
    )