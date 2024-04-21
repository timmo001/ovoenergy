"""Plan Models."""

from dataclasses import dataclass
from typing import Any


@dataclass
class OVOPlanRate:
    """Plan rate model."""

    amount: float
    currency_unit: str


@dataclass
class OVOPlanStatus:
    """Plan status model."""

    active: bool
    in_renewal: bool
    in_loss: bool
    loss_complete: bool
    has_future_contracts: bool


@dataclass
class OVOPlanUnitRate:
    """Unit rate model."""

    name: str
    unit_rate: OVOPlanRate


@dataclass
class OVOPlanElectricity:
    """Plan electricity model."""

    name: str
    exit_fee: OVOPlanRate
    contract_start_date: str
    contract_end_date: Any
    contract_type: str
    is_in_renewal: bool
    has_future_contracts: bool
    mpxn: str
    msn: str
    personal_projection: float
    standing_charge: OVOPlanRate
    unit_rates: list[OVOPlanUnitRate]


@dataclass
class OVOPlanGas:
    """Plan gas model."""

    name: str
    exit_fee: OVOPlanRate
    contract_start_date: str
    contract_end_date: Any
    contract_type: str
    is_in_renewal: bool
    has_future_contracts: bool
    mpxn: str
    msn: str
    personal_projection: float
    standing_charge: OVOPlanRate
    unit_rates: list[OVOPlanUnitRate]


@dataclass
class OVOPlans:
    """Plan model."""

    electricity: list[OVOPlanElectricity]
    gas: list[OVOPlanGas] | None
