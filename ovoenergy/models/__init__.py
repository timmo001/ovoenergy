"""Models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class OVOInterval:
    """Interval model."""

    start: datetime
    end: datetime


@dataclass
class OVOMeterReadings:
    """Meter readings model."""

    start: float
    end: float


@dataclass
class OVOCost:
    """Cost model."""

    amount: float | None
    currency_unit: str | None


@dataclass
class OVORates:
    """Rates model."""

    anytime: float | None
    standing: float | None


@dataclass
class OVODailyElectricity:
    """Daily electricity model."""

    consumption: float | None
    interval: OVOInterval | None
    meter_readings: OVOMeterReadings | None
    has_half_hour_data: bool | None
    cost: OVOCost | None
    rates: OVORates | None


@dataclass
class OVODailyGas:
    """Daily gas model."""

    consumption: float | None
    volume: float | None
    interval: OVOInterval | None
    meter_readings: OVOMeterReadings | None
    has_half_hour_data: bool | None
    cost: OVOCost | None
    rates: OVORates | None


@dataclass
class OVOHalfHour:
    """Half hour model."""

    consumption: float
    interval: OVOInterval
    unit: str


@dataclass
class OVODailyUsage:
    """Daily usage model."""

    electricity: list[OVODailyElectricity] | None
    gas: list[OVODailyGas] | None


@dataclass
class OVOHalfHourUsage:
    """Half hour usage model."""

    electricity: list[OVOHalfHour] | None
    gas: list[OVOHalfHour] | None


@dataclass
class OVOPlan:
    """Plan model."""

    standing_charge: float | None
    unit_rate: float | None
    tariff: str | None
