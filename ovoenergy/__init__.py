"""Initialize the package."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field  # pylint: disable=no-name-in-module


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

    amount: Optional[float] = Field(None, alias="amount")
    currency_unit: Optional[str] = Field(None, alias="currencyUnit")


class OVODailyElectricity(OVOBase):
    """Daily electricity model."""

    consumption: Optional[float] = Field(None, alias="consumption")
    interval: Optional[OVOInterval] = Field(None, alias="interval")
    meter_readings: Optional[OVOMeterReadings] = Field(None, alias="meterReadings")
    has_half_hour_data: Optional[bool] = Field(None, alias="hasHalfHourData")
    cost: Optional[OVOCost] = Field(None, alias="cost")


class OVODailyGas(OVOBase):
    """Daily gas model."""

    consumption: Optional[float] = Field(None, alias="consumption")
    volume: Optional[float] = Field(None, alias="volume")
    interval: Optional[OVOInterval] = Field(None, alias="interval")
    meter_readings: Optional[OVOMeterReadings] = Field(None, alias="meterReadings")
    has_half_hour_data: Optional[bool] = Field(None, alias="hasHalfHourData")
    cost: Optional[OVOCost] = Field(None, alias="cost")


class OVOHalfHour(OVOBase):
    """Half hour model."""

    consumption: float = Field(None, alias="consumption")
    interval: OVOInterval = Field(None, alias="interval")
    unit: str = Field(None, alias="unit")


class OVODailyUsage(OVOBase):
    """Daily usage model."""

    electricity: Optional[list[OVODailyElectricity]] = Field(None, alias="electricity")
    gas: Optional[list[OVODailyGas]] = Field(None, alias="gas")


class OVOHalfHourUsage(OVOBase):
    """Half hour usage model."""

    electricity: Optional[list[OVOHalfHour]] = Field(None, alias="electricity")
    gas: Optional[list[OVOHalfHour]] = Field(None, alias="gas")
