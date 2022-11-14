"""Initialize the package."""
from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Extra, Field


class OVOBase(BaseModel):
    """Base class for all OVO models."""

    class Config:
        """Pydantic config."""

        extra = Extra.allow


class OVOInterval(OVOBase):
    """Interval model."""

    start: datetime = Field(..., alias="start")
    end: datetime = Field(..., alias="end")


class OVOMeterReadings(OVOBase):
    """Meter readings model."""

    start: float = Field(..., alias="start")
    end: float = Field(..., alias="end")


class OVOCost(OVOBase):
    """Cost model."""

    amount: float = Field(..., alias="amount")
    currency_unit: str = Field(..., alias="currencyUnit")


class OVODailyElectricity(OVOBase):
    """Daily electricity model."""

    consumption: float = Field(..., alias="consumption")
    interval: OVOInterval = Field(..., alias="interval")
    meter_readings: OVOMeterReadings = Field(..., alias="meterReadings")
    has_half_hour_data: bool = Field(..., alias="hasHalfHourData")
    cost: OVOCost = Field(..., alias="cost")


class OVODailyGas(OVOBase):
    """Daily gas model."""

    consumption: float = Field(..., alias="consumption")
    volume: float = Field(..., alias="volume")
    interval: OVOInterval = Field(..., alias="interval")
    meter_readings: OVOMeterReadings = Field(..., alias="meterReadings")
    has_half_hour_data: bool = Field(..., alias="hasHalfHourData")
    cost: OVOCost = Field(..., alias="cost")


class OVOHalfHour(OVOBase):
    """Half hour model."""

    consumption: float = Field(..., alias="consumption")
    interval: OVOInterval = Field(..., alias="interval")
    unit: str = Field(..., alias="unit")


class OVODailyUsage(OVOBase):
    """Daily usage model."""

    electricity: List[OVODailyElectricity] = Field(..., alias="electricity")
    gas: List[OVODailyGas] = Field(..., alias="gas")


class OVOHalfHourUsage(OVOBase):
    """Half hour usage model."""

    electricity: List[OVOHalfHour] = Field(..., alias="electricity")
    gas: List[OVOHalfHour] = Field(..., alias="gas")
