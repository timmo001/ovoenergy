"""Get energy data from OVO's API."""
import asyncio
import json
import sys
from datetime import datetime

import aiohttp

from ovoenergy import (
    OvoCost,
    OvoDailyElectricity,
    OvoDailyGas,
    OvoDailyUsage,
    OvoHalfHour,
    OvoHalfHourUsage,
    OvoInterval,
    OvoMeterReadings,
)


class OVOEnergy:
    """Class for OVOEnergy."""

    def __init__(self) -> None:
        """Initilalize."""
        self._session = None
        self._cookies = None
        self._account_id = None
        self._customer_id = None

    async def authenticate(self, username, password) -> bool:
        """Authenticate."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        response = await self._session.post(
            "https://my.ovoenergy.com/api/v2/auth/login",
            json={"username": username, "password": password, "rememberMe": True},
        )
        response.raise_for_status()
        if response.status is not 200:
            return False

        json_response = await response.json()

        if "code" in json_response and json_response["code"] == "Unknown":
            return False
        else:
            self._cookies = response.cookies
            response = await self._session.get(
                "https://smartpaym.ovoenergy.com/api/customer-and-account-ids",
                cookies=self._cookies,
            )
            json_response = await response.json()
            if "accountIds" in json_response:
                self._account_id = json_response["accountIds"][0]
            if "customerId" in json_response:
                self._customer_id = json_response["customerId"]
        return True

    async def get_daily_usage(self, month) -> OvoDailyUsage:
        """Get daily usage data."""
        if month is None:
            return None
        electricity_usage = None
        gas_usage = None
        response = await self._session.get(
            f"https://smartpaym.ovoenergy.com/api/energy-usage/daily/{self._account_id}?date={month}",
            cookies=self._cookies,
        )
        json_response = await response.json()
        if "electricity" in json_response:
            electricity = json_response["electricity"]
            if "data" in electricity:
                electricity_usage = []
                for usage in electricity["data"]:
                    electricity_usage.append(
                        OvoDailyElectricity(
                            usage["consumption"],
                            OvoInterval(
                                datetime.strptime(
                                    usage["interval"]["start"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                                datetime.strptime(
                                    usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                            ),
                            OvoMeterReadings(
                                usage["meterReadings"]["start"],
                                usage["meterReadings"]["end"],
                            ),
                            usage["hasHhData"],
                            OvoCost(
                                usage["cost"]["amount"], usage["cost"]["currencyUnit"],
                            ),
                        )
                    )

        if "gas" in json_response:
            gas = json_response["gas"]
            if "data" in gas:
                gas_usage = []
                for usage in gas["data"]:
                    gas_usage.append(
                        OvoDailyGas(
                            usage["consumption"],
                            usage["volume"],
                            OvoInterval(
                                datetime.strptime(
                                    usage["interval"]["start"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                                datetime.strptime(
                                    usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                            ),
                            OvoMeterReadings(
                                usage["meterReadings"]["start"],
                                usage["meterReadings"]["end"],
                            ),
                            usage["hasHhData"],
                            OvoCost(
                                usage["cost"]["amount"], usage["cost"]["currencyUnit"],
                            ),
                        )
                    )

        return OvoDailyUsage(electricity_usage, gas_usage)

    async def get_half_hourly_usage(self, date) -> OvoHalfHourUsage:
        """Get half hourly usage data."""
        if date is None:
            return None
        electricity_usage = None
        gas_usage = None
        response = await self._session.get(
            f"https://smartpaym.ovoenergy.com/api/energy-usage/half-hourly/{self._account_id}?date={date}",
            cookies=self._cookies,
        )
        json_response = await response.json()
        if "electricity" in json_response:
            electricity = json_response["electricity"]
            if "data" in electricity:
                electricity_usage = []
                for usage in electricity["data"]:
                    electricity_usage.append(
                        OvoHalfHour(
                            usage["consumption"],
                            OvoInterval(
                                datetime.strptime(
                                    usage["interval"]["start"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                                datetime.strptime(
                                    usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                            ),
                            usage["unit"],
                        )
                    )
        if "gas" in json_response:
            gas = json_response["gas"]
            if "data" in gas:
                gas_usage = []
                for usage in gas["data"]:
                    gas_usage.append(
                        OvoHalfHour(
                            usage["consumption"],
                            OvoInterval(
                                datetime.strptime(
                                    usage["interval"]["start"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                                datetime.strptime(
                                    usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                ),
                            ),
                            usage["unit"],
                        )
                    )

        return OvoHalfHourUsage(electricity_usage, gas_usage)

    @property
    def account_id(self):
        return self._account_id

    @property
    def customer_id(self):
        return self._customer_id
