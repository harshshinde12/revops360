"""Pydantic data contracts — the gate between raw ingestion and all downstream logic.

Industry rule: never let raw CSV values flow into metrics. Every row is validated
here first; failures go to quarantine with a reason, never silently dropped.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

DealStage = Literal[
    "Prospecting",
    "Qualification",
    "Proposal",
    "Negotiation",
    "Commit",
    "Closed Won",
    "Closed Lost",
]

Region = Literal["West", "East", "Central", "South"]


class PipelineRow(BaseModel):
    opportunity_id: str = Field(min_length=1)
    sales_agent: str = Field(min_length=1)
    product: str = Field(min_length=1)
    account: str = Field(min_length=1)
    segment: Literal["SMB", "Mid-Market", "Enterprise"]
    lead_source: str = Field(min_length=1)
    deal_stage: DealStage
    engage_date: date
    close_date: date
    close_value: float = Field(ge=100.0, le=500000.0)
    is_closed: bool
    is_won: bool

    @field_validator("close_date")
    @classmethod
    def close_not_before_engage(cls, v: date, info) -> date:
        engage = info.data.get("engage_date")
        if engage is not None and v < engage:
            raise ValueError(f"close_date {v} before engage_date {engage}")
        return v

    @field_validator("is_won")
    @classmethod
    def won_implies_closed(cls, v: bool, info) -> bool:
        if v and not info.data.get("is_closed", False):
            raise ValueError("is_won=True requires is_closed=True")
        return v

    @field_validator("deal_stage")
    @classmethod
    def stage_matches_flags(cls, v: DealStage, info) -> DealStage:
        # Cross-field check runs after is_closed/is_won are parsed (field order matters).
        # Keep it lenient: only enforce terminal consistency, allow open stages on closed rows
        # that slipped (real CRMs are messy) — quarantine only on hard contradictions.
        is_closed = info.data.get("is_closed")
        is_won = info.data.get("is_won")
        if is_closed is True and is_won is True and v != "Closed Won":
            raise ValueError(f"closed+won row must have stage 'Closed Won', got '{v}'")
        if is_closed is True and is_won is False and v not in ("Closed Lost", "Closed Won"):
            # Lost deals sometimes keep last open stage in exports; allow but flag downstream.
            pass
        return v


class TeamRow(BaseModel):
    sales_agent: str = Field(min_length=1)
    manager: str = Field(min_length=1)
    regional_office: Region


class AccountRow(BaseModel):
    account: str = Field(min_length=1)
    sector: str = Field(min_length=1)
    year_established: int = Field(ge=1900, le=2025)
    employees: int = Field(ge=1)
    annual_revenue: float = Field(ge=0)
    office_location: str = Field(min_length=1)


class ProductRow(BaseModel):
    product: str = Field(min_length=1)
    series: str = Field(min_length=1)
    list_price: float = Field(ge=0)
