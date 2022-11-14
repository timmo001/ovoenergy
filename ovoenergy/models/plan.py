"""OVO Energy: Plan Models."""
from __future__ import annotations

from typing import Any

from pydantic import Field

from . import OVOBase


class OVOPlanRate(OVOBase):
    """Plan rate model."""

    amount: float = Field(None, alias="amount")
    currency_unit: str = Field(None, alias="currencyUnit")


class OVOPlanStatus(OVOBase):
    """Plan status model."""

    active: bool
    in_renewal: bool = Field(None, alias="inRenewal")
    in_loss: bool = Field(None, alias="inLoss")
    loss_complete: bool = Field(None, alias="lossComplete")
    has_future_contracts: bool = Field(None, alias="hasFutureContracts")


class OVOPlanUnitRate(OVOBase):
    """Unit rate model."""

    name: str = Field(None, alias="name")
    unit_rate: OVOPlanRate = Field(None, alias="unitRate")


class OVOPlanElectricity(OVOBase):
    """Plan electricity model."""

    name: str = Field(None, alias="name")
    exit_fee: OVOPlanRate = Field(None, alias="exitFee")
    contract_start_date: str = Field(None, alias="contractStartDate")
    contract_end_date: Any = Field(None, alias="contractEndDate")
    contract_type: str = Field(None, alias="contractType")
    is_in_renewal: bool = Field(None, alias="isInRenewal")
    has_future_contracts: bool = Field(None, alias="hasFutureContracts")
    mpxn: str = Field(None, alias="mpxn")
    msn: str = Field(None, alias="msn")
    personal_projection: float = Field(None, alias="personalProjection")
    standing_charge: OVOPlanRate = Field(None, alias="standingCharge")
    unit_rates: list[OVOPlanUnitRate] = Field(None, alias="unitRates")


class OVOPlanGas(OVOBase):
    """Plan gas model."""

    name: str = Field(None, alias="name")
    exit_fee: OVOPlanRate = Field(None, alias="exitFee")
    contract_start_date: str = Field(None, alias="contractStartDate")
    contract_end_date: Any = Field(None, alias="contractEndDate")
    contract_type: str = Field(None, alias="contractType")
    is_in_renewal: bool = Field(None, alias="isInRenewal")
    has_future_contracts: bool = Field(None, alias="hasFutureContracts")
    mpxn: str = Field(None, alias="mpxn")
    msn: str = Field(None, alias="msn")
    personal_projection: float = Field(None, alias="personalProjection")
    standing_charge: OVOPlanRate = Field(None, alias="standingCharge")
    unit_rates: list[OVOPlanUnitRate] = Field(None, alias="unitRates")


class OVOPlan(OVOBase):
    """Plan model."""

    electricity: OVOPlanElectricity = Field(None, alias="electricity")
    gas: OVOPlanGas = Field(None, alias="gas")
