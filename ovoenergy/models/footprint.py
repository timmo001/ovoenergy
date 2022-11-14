"""OVO Energy: Footprint Models."""
from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from . import OVOBase


class OVOFootprintElectricity(OVOBase):
    carbon_kg: float = Field(None, alias="carbonKg")
    carbon_saved_kg: float = Field(None, alias="carbonSavedKg")
    k_wh: float = Field(None, alias="kWh")


class OVOFootprintGas(OVOBase):
    carbon_kg: float = Field(None, alias="carbonKg")
    carbon_saved_kg: float = Field(None, alias="carbonSavedKg")
    k_wh: float = Field(None, alias="kWh")


class OVOFootprintBreakdown(OVOBase):
    electricity: OVOFootprintElectricity = Field(None, alias="electricity")
    gas: OVOFootprintGas = Field(None, alias="gas")


class OVOCarbonFootprint(OVOBase):
    carbon_kg: float = Field(None, alias="carbonKg")
    carbon_saved_kg: float = Field(None, alias="carbonSavedKg")
    k_wh: float = Field(None, alias="kWh")
    breakdown: OVOFootprintBreakdown = Field(None, alias="breakdown")


class OVOFootprint(OVOBase):
    from_: Optional[str] = Field(None, alias="from")
    to: Optional[str] = Field(None, alias="to")
    carbon_reduction_product_ids: Optional[List] = Field(
        None, alias="carbonReductionProductIds"
    )
    carbon_footprint: Optional[OVOCarbonFootprint] = Field(
        None, alias="carbonFootprint"
    )
