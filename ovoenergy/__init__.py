"""Get energy data from OVO's API."""

import contextlib
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
import logging
from typing import Literal
from uuid import UUID

import aiohttp

from .exceptions import (
    OVOEnergyAPINoCookies,
    OVOEnergyAPINotAuthorized,
    OVOEnergyNoAccount,
)
from .models import (
    OVOCost,
    OVODailyElectricity,
    OVODailyGas,
    OVODailyUsage,
    OVOHalfHour,
    OVOHalfHourUsage,
    OVOInterval,
    OVOMeterReadings,
)
from .models.accounts import Account, BootstrapAccounts, Supply, SupplyPointInfo
from .models.carbon_intensity import OVOCarbonIntensity, OVOCarbonIntensityForecast
from .models.footprint import (
    OVOCarbonFootprint,
    OVOFootprint,
    OVOFootprintBreakdown,
    OVOFootprintElectricity,
    OVOFootprintGas,
)
from .models.oauth import OAuth
from .models.plan import (
    OVOPlanElectricity,
    OVOPlanGas,
    OVOPlanRate,
    OVOPlans,
    OVOPlanUnitRate,
)

_LOGGER = logging.getLogger(__name__)


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
            _LOGGER.debug("OAuth token expired, refreshing: %s", self.oauth)
            await self.get_token()

            if self.oauth is None:
                raise OVOEnergyAPINotAuthorized("No OAuth token set after refresh")

            _LOGGER.debug("OAuth token refreshed: %s", self.oauth)

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

        if with_authorization and response.status in [401, 403]:
            raise OVOEnergyAPINotAuthorized(f"Not authorized: {response.status}")

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

        if not await self.get_token():
            return False

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
            access_token=json_response["accessToken"]["value"],
            expires_in=json_response["expiresIn"],
            refresh_expires_in=json_response["refreshExpiresIn"],
            # Set expires_at to current time plus expiresIn (minutes)
            expires_at=datetime.now() + timedelta(minutes=json_response["expiresIn"]),
        )

        return self._oauth

    async def bootstrap_accounts(self) -> BootstrapAccounts:
        """Bootstrap accounts."""
        response = await self._request(
            "https://smartpaymapi.ovoenergy.com/first-login/api/bootstrap/v2/",
            "GET",
        )
        json_response = await response.json()

        self._bootstrap_accounts = BootstrapAccounts(
            account_ids=json_response["accountIds"],
            customer_id=UUID(json_response["customerId"]),
            selected_account_id=json_response["selectedAccountId"],
            is_first_login=json_response.get("isFirstLogin", None),
            accounts=[
                Account(
                    account_id=account.get("accountId", None),
                    is_payg=account.get("isPayg", None),
                    is_blocked=account.get("isBlocked", None),
                    supplies=[
                        Supply(
                            mpxn=supply["mpxn"],
                            fuel=supply["fuel"],
                            is_onboarding=supply["isOnboarding"],
                            start=datetime.fromisoformat(supply["start"])
                            if supply["start"]
                            else None,
                            is_payg=supply["isPayg"],
                            supply_point_info=SupplyPointInfo(
                                meter_type=supply["supplyPointInfo"]["meterType"],
                                meter_not_found=supply["supplyPointInfo"][
                                    "meterNotFound"
                                ],
                                address=supply["supplyPointInfo"]["address"],
                            )
                            if supply["supplyPointInfo"]
                            else None,
                        )
                        for supply in account["supplies"]
                    ]
                    if "supplies" in account
                    else None
                    if "supplies" in account
                    else None,
                )
                for account in json_response["accounts"]
            ]
            if "accounts" in json_response
            else None,
        )

        return self._bootstrap_accounts

    async def get_daily_usage(
        self,
        date: str,
    ) -> OVODailyUsage:
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
                        ovo_usage.electricity.append(
                            OVODailyElectricity(
                                consumption=usage.get("consumption", None),
                                interval=OVOInterval(
                                    start=datetime.fromisoformat(
                                        usage["interval"]["start"]
                                    ),
                                    end=datetime.fromisoformat(
                                        usage["interval"]["end"]
                                    ),
                                )
                                if "interval" in usage
                                else None,
                                meter_readings=OVOMeterReadings(
                                    start=usage["meterReadings"]["start"],
                                    end=usage["meterReadings"]["end"],
                                )
                                if "meterReadings" in usage
                                else None,
                                has_half_hour_data=usage.get("hasHalfHourData", None),
                                cost=OVOCost(
                                    amount=usage["cost"]["amount"],
                                    currency_unit=usage["cost"]["currencyUnit"],
                                )
                                if "cost" in usage
                                else None,
                            )
                        )

        if "gas" in json_response:
            gas = json_response["gas"]
            if gas and "data" in gas:
                ovo_usage.gas = []
                for usage in gas["data"]:
                    if usage is not None:
                        ovo_usage.gas.append(
                            OVODailyGas(
                                consumption=usage.get("consumption", None),
                                volume=usage.get("volume", None),
                                interval=OVOInterval(
                                    start=datetime.fromisoformat(
                                        usage["interval"]["start"]
                                    ),
                                    end=datetime.fromisoformat(
                                        usage["interval"]["end"]
                                    ),
                                )
                                if "interval" in usage
                                else None,
                                meter_readings=OVOMeterReadings(
                                    start=usage["meterReadings"]["start"],
                                    end=usage["meterReadings"]["end"],
                                )
                                if "meterReadings" in usage
                                else None,
                                has_half_hour_data=usage.get("hasHalfHourData", None),
                                cost=OVOCost(
                                    amount=usage["cost"]["amount"],
                                    currency_unit=usage["cost"]["currencyUnit"],
                                ),
                            )
                        )

        return ovo_usage

    async def get_half_hourly_usage(
        self,
        date: str,
    ) -> OVOHalfHourUsage:
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
                        ovo_usage.electricity.append(
                            OVOHalfHour(
                                consumption=usage["consumption"],
                                interval=OVOInterval(
                                    start=datetime.fromisoformat(
                                        usage["interval"]["start"]
                                    ),
                                    end=datetime.fromisoformat(
                                        usage["interval"]["end"]
                                    ),
                                ),
                                unit=usage["unit"],
                            )
                        )
        if "gas" in json_response:
            gas = json_response["gas"]
            if gas and "data" in gas:
                ovo_usage.gas = []
                for usage in gas["data"]:
                    if usage is not None:
                        ovo_usage.gas.append(
                            OVOHalfHour(
                                consumption=usage["consumption"],
                                interval=OVOInterval(
                                    start=datetime.fromisoformat(
                                        usage["interval"]["start"]
                                    ),
                                    end=datetime.fromisoformat(
                                        usage["interval"]["end"]
                                    ),
                                ),
                                unit=usage["unit"],
                            )
                        )

        return ovo_usage

    async def get_plans(self) -> OVOPlans:
        """Get plans."""
        if self.account_id is None:
            raise OVOEnergyNoAccount("No account found")

        response = await self._request(
            f"https://smartpaymapi.ovoenergy.com/orex/api/plans/{self.account_id}",
            "GET",
        )
        json_response = await response.json()

        return OVOPlans(
            electricity=[
                OVOPlanElectricity(
                    name=json_response["electricity"]["name"],
                    exit_fee=OVOPlanRate(
                        amount=json_response["electricity"]["exitFee"]["amount"],
                        currency_unit=json_response["electricity"]["exitFee"][
                            "currencyUnit"
                        ],
                    ),
                    contract_start_date=json_response["electricity"][
                        "contractStartDate"
                    ],
                    contract_end_date=json_response["electricity"]["contractEndDate"],
                    contract_type=json_response["electricity"]["contractType"],
                    is_in_renewal=json_response["electricity"]["isInRenewal"],
                    has_future_contracts=json_response["electricity"][
                        "hasFutureContracts"
                    ],
                    mpxn=json_response["electricity"]["mpxn"],
                    msn=json_response["electricity"]["msn"],
                    personal_projection=json_response["electricity"][
                        "personalProjection"
                    ],
                    standing_charge=OVOPlanRate(
                        amount=json_response["electricity"]["standingCharge"]["amount"],
                        currency_unit=json_response["electricity"]["standingCharge"][
                            "currencyUnit"
                        ],
                    ),
                    unit_rates=[
                        OVOPlanUnitRate(
                            name=unit_rate["name"],
                            unit_rate=OVOPlanRate(
                                amount=unit_rate["unitRate"]["amount"],
                                currency_unit=unit_rate["unitRate"]["currencyUnit"],
                            ),
                        )
                        for unit_rate in json_response["electricity"]["unitRates"]
                    ],
                )
                for json_response in json_response["electricity"]
            ],
            gas=[
                OVOPlanGas(
                    name=json_response["gas"]["name"],
                    exit_fee=OVOPlanRate(
                        amount=json_response["gas"]["exitFee"]["amount"],
                        currency_unit=json_response["gas"]["exitFee"]["currencyUnit"],
                    ),
                    contract_start_date=json_response["gas"]["contractStartDate"],
                    contract_end_date=json_response["gas"]["contractEndDate"],
                    contract_type=json_response["gas"]["contractType"],
                    is_in_renewal=json_response["gas"]["isInRenewal"],
                    has_future_contracts=json_response["gas"]["hasFutureContracts"],
                    mpxn=json_response["gas"]["mpxn"],
                    msn=json_response["gas"]["msn"],
                    personal_projection=json_response["gas"]["personalProjection"],
                    standing_charge=OVOPlanRate(
                        amount=json_response["gas"]["standingCharge"]["amount"],
                        currency_unit=json_response["gas"]["standingCharge"][
                            "currencyUnit"
                        ],
                    ),
                    unit_rates=[
                        OVOPlanUnitRate(
                            name=unit_rate["name"],
                            unit_rate=OVOPlanRate(
                                amount=unit_rate["unitRate"]["amount"],
                                currency_unit=unit_rate["unitRate"]["currencyUnit"],
                            ),
                        )
                        for unit_rate in json_response["gas"]["unitRates"]
                    ],
                )
                for json_response in json_response["gas"]
            ]
            if "gas" in json_response
            else None,
        )

    async def get_footprint(self) -> OVOFootprint:
        """Get footprint."""
        if self.account_id is None:
            raise OVOEnergyNoAccount("No account found")

        response = await self._request(
            f"https://smartpaymapi.ovoenergy.com/carbon-api/{self.account_id}/footprint",
            "GET",
        )
        json_response = await response.json()

        return OVOFootprint(
            from_=json_response["from"],
            to=json_response["to"],
            carbon_reduction_product_ids=json_response["carbonReductionProductIds"],
            carbon_footprint=OVOCarbonFootprint(
                carbon_kg=json_response["carbonFootprint"]["carbonKg"],
                carbon_saved_kg=json_response["carbonFootprint"]["carbonSavedKg"],
                k_wh=json_response["carbonFootprint"]["kWh"],
                breakdown=OVOFootprintBreakdown(
                    electricity=OVOFootprintElectricity(
                        carbon_kg=json_response["carbonFootprint"]["breakdown"][
                            "electricity"
                        ]["carbonKg"],
                        carbon_saved_kg=json_response["carbonFootprint"]["breakdown"][
                            "electricity"
                        ]["carbonSavedKg"],
                        k_wh=json_response["carbonFootprint"]["breakdown"][
                            "electricity"
                        ]["kWh"],
                    ),
                    gas=OVOFootprintGas(
                        carbon_kg=json_response["carbonFootprint"]["breakdown"]["gas"][
                            "carbonKg"
                        ],
                        carbon_saved_kg=json_response["carbonFootprint"]["breakdown"][
                            "gas"
                        ]["carbonSavedKg"],
                        k_wh=json_response["carbonFootprint"]["breakdown"]["gas"][
                            "kWh"
                        ],
                    ),
                ),
            ),
        )

    async def get_carbon_intensity(self):
        """Get carbon intensity."""
        response = await self._request(
            "https://smartpaymapi.ovoenergy.com/carbon-bff/carbonintensity",
            "GET",
        )
        json_response = await response.json()

        return OVOCarbonIntensity(
            forecast=[
                OVOCarbonIntensityForecast(
                    time_from=forecast["from"],
                    intensity=forecast["intensity"],
                    level=forecast["level"],
                    colour=forecast["colour"],
                    colour_v2=forecast["colourV2"],
                )
                for forecast in json_response["forecast"]
            ],
            current=json_response["current"],
            greentime=json_response["greentime"],
        )
