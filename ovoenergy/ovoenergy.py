"""OVO Energy: Get energy data from OVO's API."""
from __future__ import annotations

from http.cookies import SimpleCookie
from typing import Optional

import aiohttp

from .models import (
    OVODailyElectricity,
    OVODailyGas,
    OVODailyUsage,
    OVOHalfHour,
    OVOHalfHourUsage,
)
from .models.carbon_intensity import OVOCarbonIntensity
from .models.footprint import OVOFootprint
from .models.plan import OVOPlan


class OVOEnergy:
    """Class for OVOEnergy."""

    def __init__(self) -> None:
        """Initilalize."""
        self._account_id: Optional[str] = None
        self._account_ids: list[str] = []
        self._cookies: Optional[SimpleCookie[str]] = None
        self._customer_id: Optional[str] = None
        self._username: Optional[str] = None

    @property
    def account_id(self):
        """Return account id."""
        return self._account_id

    @account_id.setter
    def account_id(
        self,
        new_account: str,
    ):
        """Set account id."""
        if new_account in self._account_ids:
            self._account_id = new_account
        else:
            raise ValueError("Invalid account ID")

    @property
    def account_ids(self):
        """Return account ids."""
        return self._account_ids

    @property
    def customer_id(self):
        """Return customer id."""
        return self._customer_id

    @property
    def username(self):
        """Return username."""
        return self._username

    async def authenticate(self, username, password, account=None) -> bool:
        """Authenticate."""
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                "https://my.ovoenergy.com/api/v2/auth/login",
                json={
                    "username": username,
                    "password": password,
                    "rememberMe": True,
                },
            )

            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError:
                pass

            if response.status != 200:
                return False
            json_response = await response.json()

            if "code" in json_response and json_response["code"] == "Unknown":
                return False
            self._cookies = response.cookies
            response = await session.get(
                "https://smartpaym.ovoenergy.com/api/customer-and-account-ids",
                cookies=self._cookies,
            )
            json_response = await response.json()
            if "accountIds" in json_response:
                self._account_ids = json_response["accountIds"]

                if account:
                    if account in self._account_ids:
                        self._account_id = account
                    else:
                        return False
                else:
                    self._account_id = self._account_ids[0]
            if "customerId" in json_response:
                self._customer_id = json_response["customerId"]
            self._username = username

        return True

    async def get_daily_usage(
        self,
        date: str,
    ) -> Optional[OVODailyUsage]:
        """Get daily usage data."""
        if date is None:
            return None

        ovo_usage = OVODailyUsage()

        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"https://smartpaymapi.ovoenergy.com/usage/api/daily/{self._account_id}?date={date}",
                cookies=self._cookies,
            )
            json_response = await response.json()

        if "electricity" in json_response:
            electricity = json_response["electricity"]
            if electricity and "data" in electricity:
                ovo_usage.electricity = []
                for usage in electricity["data"]:
                    if usage is not None:
                        ovo_usage.electricity.append(OVODailyElectricity(**usage))

        if "gas" in json_response:
            gas = json_response["gas"]
            if gas and "data" in gas:
                ovo_usage.gas = []
                for usage in gas["data"]:
                    if usage is not None:
                        ovo_usage.gas.append(OVODailyGas(**usage))

        return ovo_usage

    async def get_half_hourly_usage(
        self,
        date: str,
    ) -> Optional[OVOHalfHourUsage]:
        """Get half hourly usage data."""
        if date is None:
            return None

        ovo_usage = OVOHalfHourUsage()

        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"https://smartpaymapi.ovoenergy.com/usage/api/half-hourly/{self._account_id}?date={date}",
                cookies=self._cookies,
            )
            json_response = await response.json()

        if "electricity" in json_response:
            electricity = json_response["electricity"]
            if electricity and "data" in electricity:
                ovo_usage.electricity = []
                for usage in electricity["data"]:
                    if usage is not None:
                        ovo_usage.electricity.append(OVOHalfHour(**usage))
        if "gas" in json_response:
            gas = json_response["gas"]
            if gas and "data" in gas:
                ovo_usage.gas = []
                for usage in gas["data"]:
                    if usage is not None:
                        ovo_usage.gas.append(OVOHalfHour(**usage))

        return ovo_usage

    async def get_plan(self) -> OVOPlan:
        """Get plan."""
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"https://smartpaymapi.ovoenergy.com/orex/api/plans/{self._account_id}",
                cookies=self._cookies,
            )
            json_response = await response.json()

        return OVOPlan(**json_response)

    async def get_footprint(self) -> OVOFootprint:
        """Get footprint."""
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"https://smartpaymapi.ovoenergy.com/carbon-api/{self._account_id}/footprint",
                cookies=self._cookies,
            )
            json_response = await response.json()

        return OVOFootprint(**json_response)

    async def get_carbon_intensity(self):
        """Get carbon intensity."""
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                "https://smartpaymapi.ovoenergy.com/carbon-bff/carbonintensity",
                cookies=self._cookies,
            )
            json_response = await response.json()

        return OVOCarbonIntensity(**json_response)
