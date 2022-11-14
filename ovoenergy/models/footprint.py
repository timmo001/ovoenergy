"""OVO Energy: Footprint Models."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from . import OVOBase


class OVOFootprintElectricity(OVOBase):
    """Electricity footprint model."""

    carbon_kg: float = Field(None, alias="carbonKg")
    carbon_saved_kg: float = Field(None, alias="carbonSavedKg")
    k_wh: float = Field(None, alias="kWh")


class OVOFootprintGas(OVOBase):
    """Gas footprint model."""

    carbon_kg: float = Field(None, alias="carbonKg")
    carbon_saved_kg: float = Field(None, alias="carbonSavedKg")
    k_wh: float = Field(None, alias="kWh")


class OVOFootprintBreakdown(OVOBase):
    """Footprint breakdown model."""

    electricity: OVOFootprintElectricity = Field(None, alias="electricity")
    gas: OVOFootprintGas = Field(None, alias="gas")


class OVOCarbonFootprint(OVOBase):
    """Carbon footprint model."""

    carbon_kg: float = Field(None, alias="carbonKg")
    carbon_saved_kg: float = Field(None, alias="carbonSavedKg")
    k_wh: float = Field(None, alias="kWh")
    breakdown: OVOFootprintBreakdown = Field(None, alias="breakdown")


class OVOFootprint(OVOBase):
    """Footprint model."""

    from_: Optional[str] = Field(None, alias="from")
    to: Optional[str] = Field(None, alias="to")
    carbon_reduction_product_ids: list[Any] = Field(
        None, alias="carbonReductionProductIds"
    )
    carbon_footprint: Optional[OVOCarbonFootprint] = Field(
        None, alias="carbonFootprint"
    )
