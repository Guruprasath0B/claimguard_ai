# schemas/claim.py

from typing import List, Optional

from pydantic import BaseModel, Field


class ClaimLineItem(BaseModel):
    code: Optional[str] = None
    description: str
    amount: float = Field(ge=0)


class ClaimData(BaseModel):
    claim_id: str
    patient_identifier: str
    policy_number: Optional[str] = None

    diagnosis: Optional[str] = None
    procedure: Optional[str] = None

    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None

    sum_insured: float = Field(ge=0)
    requested_amount: float = Field(ge=0)

    room_rent_per_day: Optional[float] = Field(
        default=None,
        ge=0,
    )

    room_rent_cap_percent: float = Field(
        default=1.0,
        ge=0,
    )

    line_items: List[ClaimLineItem] = Field(
        default_factory=list
    )

    non_medical_amount: float = Field(
        default=0.0,
        ge=0,
    )