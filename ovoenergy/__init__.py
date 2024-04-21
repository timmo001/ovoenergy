"""Get energy data from OVO's API."""

import contextlib
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from typing import Literal
from uuid import UUID

import aiohttp

from .exceptions import (
    OVOEnergyAPINoCookies,
    OVOEnergyAPINotAuthorized,
    OVOEnergyNoAccount,
)
from .models import (
    OVODailyElectricity,
    OVODailyGas,
    OVODailyUsage,
    OVOHalfHour,
    OVOHalfHourUsage,
)
from .models.accounts import BootstrapAccounts
from .models.carbon_intensity import OVOCarbonIntensity
from .models.footprint import OVOFootprint
from .models.oauth import OAuth
from .models.plan import OVOPlan


class OVOEnergy:
    """Class for OVOEnergy."""

    custom_account_id: int | None = None

    def __init__(
        self,
        client_session: aiohttp.ClientSession,
    ) -> None:
        """Initilalize."""
        self._client_session = client_session

        self._bootstrap_accounts: BootstrapAccounts | None = None
        self._cookies: SimpleCookie | None = None
        self._oauth: OAuth | None = None
        self._username: str | None = None

    @property
    def account_id(self) -> int | None:
        """Return account id."""
        if (
            self.custom_account_id is not None
            and self.account_ids is not None
            and self.custom_account_id not in set(self.account_ids)
        ):
            raise OVOEnergyNoAccount("Custom account not found in accounts")

        return (
            self.custom_account_id
            if self.custom_account_id is not None
            else self._bootstrap_accounts.selected_account_id
            if self._bootstrap_accounts
            else None
        )

    @property
    def account_ids(self) -> list[int] | None:
        """Return account ids."""
        return (
            self._bootstrap_accounts.account_ids if self._bootstrap_accounts else None
        )

    @property
    def customer_id(self) -> UUID | None:
        """Return customer id."""
        return (
            self._bootstrap_accounts.customer_id if self._bootstrap_accounts else None
        )

    @property
    def oauth(self) -> OAuth | None:
        """Return OAuth."""
        return self._oauth

    @property
    def oauth_expired(self) -> bool:
        """Return True if OAuth token has expired."""
        return self.oauth is None or self.oauth.expires_at < datetime.now()

    @property
    def username(self) -> str | None:
        """Return username."""
        return self._username

    async def _request(
        self,
        url: str,
        method: Literal["GET"] | Literal["POST"],
        with_cookies: bool = True,
        with_authorization: bool = True,
        **kwargs,
    ):
        """Request."""
        if with_cookies and self._cookies is None:
            raise OVOEnergyAPINoCookies("No cookies set")
        if with_authorization and self._oauth is None:
            raise OVOEnergyAPINotAuthorized("No OAuth token set")

        if with_authorization and self.oauth_expired:
            await self.get_token()

        if self.oauth is None:
            raise OVOEnergyAPINotAuthorized("No OAuth token set after refresh")

        response = await self._client_session.request(
            method,
            url,
            cookies=self._cookies if with_cookies else None,
            headers={
                "Authorization": f"Bearer {self.oauth.access_token}"
                if self.oauth
                else None
            }
            if with_authorization
            else None,
            **kwargs,
        )
        with contextlib.suppress(aiohttp.ClientResponseError):
            response.raise_for_status()

        return response

    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> bool:
        """Authenticate."""
        response = await self._request(
            "https://my.ovoenergy.com/api/v2/auth/login",
            "POST",
            json={
                "username": username,
                "password": password,
                "rememberMe": True,
            },
            with_cookies=False,
            with_authorization=False,
        )
        if response.status != 200:
            return False

        json_response = await response.json()

        if "code" in json_response and json_response["code"] == "Unknown":
            return False

        self._cookies = response.cookies
        self._username = username

        await self.bootstrap_accounts()

        return True

    async def get_token(self) -> OAuth | Literal[False]:
        """Get token."""
        response = await self._request(
            "https://my.ovoenergy.com/api/v2/auth/token",
            "GET",
            with_authorization=False,
        )
        if response.status != 200:
            return False

        json_response = await response.json()

        self._oauth = OAuth(
            access_token=json_response["expires_in"]["access_token"],
            expires_in=json_response["expires_in"],
            refresh_expires_in=json_response["refresh_expires_in"],
            # Set expires_at to current time plus expires_in (minutes)
            expires_at=datetime.now() + timedelta(minutes=json_response["expires_in"]),
        )

        return self._oauth

    async def bootstrap_accounts(self) -> None:
        """Bootstrap accounts."""
        response = await self._request(
            "https://smartpaymapi.ovoenergy.com/first-login/api/bootstrap/v2/",
            "GET",
        )
        json_response = await response.json()

        self._bootstrap_accounts = BootstrapAccounts(**json_response)

    async def get_daily_usage(
        self,
        date: str,
    ) -> OVODailyUsage | None:
        """Get daily usage data."""
        if self.account_id is None:
            raise OVOEnergyNoAccount("No account found")

        ovo_usage = OVODailyUsage(
            electricity=None,
            gas=None,
        )

        response = await self._request(
            f"https://smartpaymapi.ovoenergy.com/usage/api/daily/{self.account_id}?date={date}",
            "GET",
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
    ) -> OVOHalfHourUsage | None:
        """Get half hourly usage data."""
        if self.account_id is None:
            raise OVOEnergyNoAccount("No account found")

        ovo_usage = OVOHalfHourUsage(
            electricity=None,
            gas=None,
        )

        response = await self._request(
            f"https://smartpaymapi.ovoenergy.com/usage/api/half-hourly/{self.account_id}?date={date}",
            "GET",
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
        if self.account_id is None:
            raise OVOEnergyNoAccount("No account found")

        response = await self._request(
            f"https://smartpaymapi.ovoenergy.com/orex/api/plans/{self.account_id}",
            "GET",
        )
        json_response = await response.json()

        return OVOPlan(**json_response)

    async def get_footprint(self) -> OVOFootprint:
        """Get footprint."""
        if self.account_id is None:
            raise OVOEnergyNoAccount("No account found")

        response = await self._request(
            f"https://smartpaymapi.ovoenergy.com/carbon-api/{self.account_id}/footprint",
            "GET",
        )
        json_response = await response.json()

        return OVOFootprint(**json_response)

    async def get_carbon_intensity(self):
        """Get carbon intensity."""
        response = await self._request(
            "https://smartpaymapi.ovoenergy.com/carbon-bff/carbonintensity",
            "GET",
        )
        json_response = await response.json()

        return OVOCarbonIntensity(**json_response)
