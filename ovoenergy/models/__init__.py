"""OVO Energy: Models."""
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

    start: datetime = Field(None, alias="start")
    end: datetime = Field(None, alias="end")


class OVOMeterReadings(OVOBase):
    """Meter readings model."""

    start: float = Field(None, alias="start")
    end: float = Field(None, alias="end")


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

    electricity: list[OVODailyElectricity] = Field([], alias="electricity")
    gas: list[OVODailyGas] = Field([], alias="gas")


class OVOHalfHourUsage(OVOBase):
    """Half hour usage model."""

    electricity: list[OVOHalfHour] = Field([], alias="electricity")
    gas: list[OVOHalfHour] = Field([], alias="gas")


class OVOPlan(OVOBase):
    """Plan model."""

    standing_charge: Optional[float] = Field(None, alias="standingCharge")
    unit_rate: Optional[float] = Field(None, alias="unitRate")
    tariff: Optional[str] = Field(None, alias="tariff")
