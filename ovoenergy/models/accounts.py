"""Dataclasses for the bootstrap/accounts endpoint."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID


@dataclass
class SupplyPointInfo:
    """Supply point info model."""

    meter_type: str | None = None
    meter_not_found: bool | None = None
    address: list[str] | None = None


@dataclass
class Supply:
    """Supply model."""

    mpxn: str | None
    fuel: Literal["ELECTRICITY", "GAS"] | str | None
    is_onboarding: bool | None
    start: datetime | None
    is_payg: bool | None
    supply_point_info: SupplyPointInfo | None


@dataclass
class Account:
    """Account model."""

    account_id: int
    is_payg: bool | None
    is_blocked: bool | None
    supplies: list[Supply] | None


@dataclass
class BootstrapAccounts:
    """Bootstrap Accounts model."""

    account_ids: list[int]
    customer_id: UUID
    selected_account_id: int
    accounts: list[Account] | None
    is_first_login: bool | None
