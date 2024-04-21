"""Footprint Models."""

from dataclasses import dataclass
from typing import Any


@dataclass
class OVOFootprintElectricity:
    """Electricity footprint model."""

    carbon_kg: float
    carbon_saved_kg: float
    k_wh: float


@dataclass
class OVOFootprintGas:
    """Gas footprint model."""

    carbon_kg: float
    carbon_saved_kg: float
    k_wh: float


@dataclass
class OVOFootprintBreakdown:
    """Footprint breakdown model."""

    electricity: OVOFootprintElectricity
    gas: OVOFootprintGas


@dataclass
class OVOCarbonFootprint:
    """Carbon footprint model."""

    carbon_kg: float
    carbon_saved_kg: float
    k_wh: float
    breakdown: OVOFootprintBreakdown


@dataclass
class OVOFootprint:
    """Footprint model."""

    from_: str | None
    to: str | None
    carbon_reduction_product_ids: list[Any]
    carbon_footprint: OVOCarbonFootprint | None
