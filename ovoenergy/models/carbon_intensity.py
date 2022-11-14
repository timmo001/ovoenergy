"""OVO Energy: Footprint Models."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from . import OVOBase


class OVOCarbonIntensityForecast(OVOBase):
    """Carbon intensity forecast model."""

    time_from: str = Field(None, alias="from")
    intensity: float = Field(None, alias="intensity")
    level: str = Field(None, alias="level")
    colour: str = Field(None, alias="color")
    colour_v2: str = Field(None, alias="colourV2")


class OVOCarbonIntensity(OVOBase):
    """Carbon intensity model."""

    forecast: list[OVOCarbonIntensityForecast] = Field([], alias="forecast")
    current: Optional[str] = Field(None, alias="current")
    greentime: Optional[Any] = Field(None, alias="greentime")
