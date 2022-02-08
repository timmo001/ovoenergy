"""Get energy data from OVO's API."""
from datetime import datetime, timedelta

import aiohttp

from ovoenergy import (
    OVOCost,
    OVODailyElectricity,
    OVODailyGas,
    OVODailyUsage,
    OVOHalfHour,
    OVOHalfHourUsage,
    OVOInterval,
    OVOMeterReadings,
)


class OVOEnergy:
    """Class for OVOEnergy."""

    def __init__(self) -> None:
        """Initilalize."""
        self._account_id = None
        self._account_ids = None
        self._cookies = None
        self._customer_id = None
        self._username = None

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
            except:
                pass

            if response.status is not 200:
                return False
            json_response = await response.json()

            if "code" in json_response and json_response["code"] == "Unknown":
                return False
            else:
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

    async def get_daily_usage(self, month: str) -> OVODailyUsage:
        """Get daily usage data."""
        if month is None:
            return None
        electricity_usage = None
        gas_usage = None

        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"https://smartpaym.ovoenergy.com/api/energy-usage/daily/{self._account_id}?date={month}",
                cookies=self._cookies,
            )
            json_response = await response.json()

        if "electricity" in json_response:
            electricity = json_response["electricity"]
            if electricity and "data" in electricity:
                electricity_usage = []
                for usage in electricity["data"]:
                    if usage is not None:
                        electricity_usage.append(
                            OVODailyElectricity(
                                usage["consumption"]
                                if "consumption" in usage
                                else None,
                                OVOInterval(
                                    datetime.strptime(
                                        usage["interval"]["start"],
                                        "%Y-%m-%dT%H:%M:%S.%f",
                                    ),
                                    datetime.strptime(
                                        usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                    ),
                                )
                                if "interval" in usage
                                and "start" in usage["interval"]
                                and "end" in usage["interval"]
                                else None,
                                OVOMeterReadings(
                                    usage["meterReadings"]["start"],
                                    usage["meterReadings"]["end"],
                                )
                                if "meterReadings" in usage
                                else None,
                                usage["hasHhData"] if "hasHhData" in usage else None,
                                OVOCost(
                                    usage["cost"]["amount"],
                                    usage["cost"]["currencyUnit"],
                                )
                                if "cost" in usage
                                else None,
                            )
                        )

        if "gas" in json_response:
            gas = json_response["gas"]
            if gas and "data" in gas:
                gas_usage = []
                for usage in gas["data"]:
                    if usage is not None:
                        gas_usage.append(
                            OVODailyGas(
                                usage["consumption"]
                                if "consumption" in usage
                                else None,
                                usage["volume"] if "volume" in usage else None,
                                OVOInterval(
                                    datetime.strptime(
                                        usage["interval"]["start"],
                                        "%Y-%m-%dT%H:%M:%S.%f",
                                    ),
                                    datetime.strptime(
                                        usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                    ),
                                )
                                if "interval" in usage
                                and "start" in usage["interval"]
                                and "end" in usage["interval"]
                                else None,
                                OVOMeterReadings(
                                    usage["meterReadings"]["start"],
                                    usage["meterReadings"]["end"],
                                )
                                if "meterReadings" in usage
                                else None,
                                usage["hasHhData"] if "hasHhData" in usage else None,
                                OVOCost(
                                    usage["cost"]["amount"],
                                    usage["cost"]["currencyUnit"],
                                )
                                if "cost" in usage
                                else None,
                            )
                        )

        return OVODailyUsage(electricity_usage, gas_usage)

    async def get_half_hourly_usage(self, date: str) -> OVOHalfHourUsage:
        """Get half hourly usage data."""
        if date is None:
            return None
        electricity_usage = None
        gas_usage = None

        async with aiohttp.ClientSession() as session:
            response = await session.get(
                f"https://smartpaym.ovoenergy.com/api/energy-usage/half-hourly/{self._account_id}?date={date}",
                cookies=self._cookies,
            )
            json_response = await response.json()

        if "electricity" in json_response:
            electricity = json_response["electricity"]
            if electricity and "data" in electricity:
                electricity_usage = []
                for usage in electricity["data"]:
                    if usage is not None:
                        electricity_usage.append(
                            OVOHalfHour(
                                usage["consumption"]
                                if "consumption" in usage
                                else None,
                                OVOInterval(
                                    datetime.strptime(
                                        usage["interval"]["start"],
                                        "%Y-%m-%dT%H:%M:%S.%f",
                                    ),
                                    datetime.strptime(
                                        usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                    ),
                                )
                                if "interval" in usage
                                and "start" in usage["interval"]
                                and "end" in usage["interval"]
                                else None,
                                usage["unit"] if "unit" in usage else None,
                            )
                        )
        if "gas" in json_response:
            gas = json_response["gas"]
            if gas and "data" in gas:
                gas_usage = []
                for usage in gas["data"]:
                    if usage is not None:
                        gas_usage.append(
                            OVOHalfHour(
                                usage["consumption"]
                                if "consumption" in usage
                                else None,
                                OVOInterval(
                                    datetime.strptime(
                                        usage["interval"]["start"],
                                        "%Y-%m-%dT%H:%M:%S.%f",
                                    ),
                                    datetime.strptime(
                                        usage["interval"]["end"], "%Y-%m-%dT%H:%M:%S.%f"
                                    ),
                                )
                                if "interval" in usage
                                and "start" in usage["interval"]
                                and "end" in usage["interval"]
                                else None,
                                usage["unit"] if "unit" in usage else None,
                            )
                        )

        return OVOHalfHourUsage(electricity_usage, gas_usage)

    async def get_last_reading(self, date: datetime = None) -> OVOHalfHourUsage:
        date = date if date is not None else datetime.utcnow()
        print(f"DATE: {date}")
        usage: OVOHalfHourUsage = await self.get_half_hourly_usage(
            date.strftime("%Y-%m-%d")
        )
        if usage is None or usage.electricity is None or len(usage.electricity) == 0:
            date = date - timedelta(days=1)
            if date is datetime.utcnow() - timedelta(days=7):
                return None
            return await self.get_last_reading(date)
        return usage

    @property
    def account_id(self):
        return self._account_id

    @account_id.setter
    def account_id(self, new_account):
        if new_account in self._account_ids:
            self._account_id = new_account
        else:
            print("Invalid account ID")

    @property
    def account_ids(self):
        return self._account_ids

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def username(self):
        return self._username
