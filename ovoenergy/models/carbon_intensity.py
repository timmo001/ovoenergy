"""Footprint Models."""

from dataclasses import dataclass
from typing import Any


@dataclass
class OVOCarbonIntensityForecast:
    """Carbon intensity forecast model."""

    time_from: str
    intensity: float
    level: str
    colour: str
    colour_v2: str


@dataclass
class OVOCarbonIntensity:
    """Carbon intensity model."""

    forecast: list[OVOCarbonIntensityForecast]
    current: str | None
    greentime: Any | None
