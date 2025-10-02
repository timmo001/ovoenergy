"""Get energy data from OVO's API."""

import contextlib
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
import logging
from typing import Literal
from uuid import UUID

import aiohttp
import jwt

from .const import (
    AUTH_LOGIN_URL,
    AUTH_TOKEN_URL,
    BOOTSTRAP_GRAPHQL_URL,
    BOOTSTRAP_QUERY,
    CARBON_FOOTPRINT_URL,
    CARBON_INTENSITY_URL,
    USAGE_DAILY_URL,
    USAGE_HALF_HOURLY_URL,
)
from .exceptions import (
    OVOEnergyAPIInvalidResponse,
    OVOEnergyAPINoCookies,
    OVOEnergyAPINotAuthorized,
    OVOEnergyAPINotFound,
    OVOEnergyNoAccount,
    OVOEnergyNoCustomer,
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
    OVORates,
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

        self._customer_id: UUID | None = None
        self._bootstrap_accounts: BootstrapAccounts | None = None
        self._cookies: SimpleCookie | None = None
        self._oauth: OAuth | None = None
        self._username: str | None = None
        self._account_ids: list[int] | None = None

    @property
    def account_id(self) -> int | None:
        """Return account id."""
        if self.custom_account_id is None and (
            self.account_ids is None or len(self.account_ids) == 0
        ):
            raise OVOEnergyNoAccount("No account id set")

        return (
            self.custom_account_id
            if self.custom_account_id
            else self.account_ids[0]
            if self.account_ids and len(self.account_ids) > 0
            else None
        )

    @property
    def account_ids(self) -> list[int] | None:
        """Return account ids."""
        return self._account_ids

    @property
    def customer_id(self) -> UUID | None:
        """Return customer id."""
        if self._customer_id is None:
            raise OVOEnergyNoCustomer("No customer id set")

        return self._customer_id

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

            if not await self.get_token() or self.oauth is None:
                raise OVOEnergyAPINotAuthorized("No OAuth token set after refresh")

            _LOGGER.debug("OAuth token refreshed: %s", self.oauth)

        response = await self._client_session.request(
            method,
            url,
            cookies=self._cookies if with_cookies else None,
            headers=(
                {
                    "Authorization": f"Bearer {self.oauth.access_token}",
                }
                if with_authorization and self.oauth
                else None
            ),
            **kwargs,
        )
        with contextlib.suppress(aiohttp.ClientResponseError):
            response.raise_for_status()

        if with_authorization and response.status in [401, 403]:
            raise OVOEnergyAPINotAuthorized(f"Not authorized: {response.status}")

        if response.status == 404:
            raise OVOEnergyAPINotFound(f"Endpoint not found: {response.status}")

        return response

    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> bool:
        """Authenticate."""
        response = await self._request(
            AUTH_LOGIN_URL,
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
            AUTH_TOKEN_URL,
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

        # Read JWT token
        decoded_token = jwt.decode(
            self._oauth.access_token, options={"verify_signature": False}
        )

        # Set customer id from sub claim
        self._customer_id = decoded_token.get("sub")

        # Set fallback account ids from permissions array if it is set
        ids: list[int] = []
        for permission in decoded_token.get("permissions", []):
            if "account::" not in permission:
                continue
            account_id = permission.split("account::")[1]
            if not account_id.isdigit():
                continue
            ids.append(int(account_id))

        # Set fallback account ids if they are set
        if len(ids) > 0:
            self._account_ids = ids
        else:
            self._account_ids = None

        return self._oauth

    async def bootstrap_accounts(self) -> BootstrapAccounts:
        """Bootstrap accounts."""
        response = await self._request(
            BOOTSTRAP_GRAPHQL_URL,
            "POST",
            json={
                "operationName": "Bootstrap",
                "query": BOOTSTRAP_QUERY,
                "variables": {
                    "customerId": self.customer_id,
                },
            },
        )
        json_response = await response.json()

        if "data" not in json_response:
            raise OVOEnergyAPIInvalidResponse("Missing 'data' key in response")
        if "customer_nextV1" not in json_response["data"]:
            raise OVOEnergyAPIInvalidResponse(
                "Missing 'data.customer_nextV1' key in response"
            )
        if "id" not in json_response["data"]["customer_nextV1"]:
            raise OVOEnergyAPIInvalidResponse(
                "Missing 'data.customer_nextV1.id' key in response"
            )
        if (
            "customerAccountRelationships"
            not in json_response["data"]["customer_nextV1"]
        ):
            raise OVOEnergyAPIInvalidResponse(
                "Missing 'data.customer_nextV1.customerAccountRelationships' key in response"
            )
        if (
            "edges"
            not in json_response["data"]["customer_nextV1"][
                "customerAccountRelationships"
            ]
        ):
            raise OVOEnergyAPIInvalidResponse(
                "Missing 'data.customer_nextV1.customerAccountRelationships.edges' key in response"
            )

        accounts: list[Account] = []
        for edge in json_response["data"]["customer_nextV1"][
            "customerAccountRelationships"
        ]["edges"]:
            if "node" not in edge:
                _LOGGER.warning(
                    "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node' key in response"
                )
                continue
            if "account" not in edge["node"]:
                _LOGGER.warning(
                    "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node.account' key in response"
                )
                continue

            if "id" not in edge["node"]["account"]:
                _LOGGER.warning(
                    "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node.account.id' key in response"
                )
                continue

            if "accountSupplyPoints" not in edge["node"]["account"]:
                _LOGGER.warning(
                    "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node.account.accountSupplyPoints' key in response"
                )
                continue

            supplies: list[Supply] = []
            for supply in edge["node"]["account"]["accountSupplyPoints"]:
                if "supplyPoint" not in supply:
                    _LOGGER.warning(
                        "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node.account.accountSupplyPoints[X].supplyPoint' key in response"
                    )
                    continue

                if "meterTechnicalDetails" not in supply["supplyPoint"]:
                    _LOGGER.warning(
                        "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node.account.accountSupplyPoints[X].supplyPoint.meterTechnicalDetails' key in response"
                    )
                    continue

                active_meter_technical_details = None
                for meter_detail in supply["supplyPoint"]["meterTechnicalDetails"]:
                    if "status" not in meter_detail:
                        _LOGGER.warning(
                            "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node.account.accountSupplyPoints[X].supplyPoint.meterTechnicalDetails[X].status' key in response"
                        )
                        continue

                    if meter_detail["status"].lower() == "active":
                        active_meter_technical_details = meter_detail
                        break

                supply_point_address_lines: list[str] = []
                if "address" not in supply["supplyPoint"]:
                    _LOGGER.warning(
                        "Missing 'data.customer_nextV1.customerAccountRelationships.edges[X].node.account.accountSupplyPoints[X].supplyPoint.address' key in response. Allowing empty address."
                    )
                else:
                    supply_point_address_lines = supply["supplyPoint"]["address"].get(
                        "addressLines", []
                    )
                    if "postCode" in supply["supplyPoint"]["address"]:
                        supply_point_address_lines.append(
                            supply["supplyPoint"]["address"].get("postCode")
                        )

                supplies.append(
                    Supply(
                        mpxn=active_meter_technical_details["meterSerialNumber"]
                        if active_meter_technical_details
                        else None,
                        fuel=supply["supplyPoint"].get("fuelType", None),
                        is_onboarding=supply["supplyPoint"].get("isOnboarding", None),
                        start=supply["supplyPoint"].get("startDate", None),
                        is_payg=supply["supplyPoint"].get("isPayg", None),
                        supply_point_info=SupplyPointInfo(
                            meter_type=active_meter_technical_details["type"]
                            if active_meter_technical_details
                            else None,
                            meter_not_found=active_meter_technical_details[
                                "status"
                            ].lower()
                            == "removed"
                            if active_meter_technical_details
                            else None,
                            address=supply_point_address_lines,
                        ),
                    )
                )

            accounts.append(
                Account(
                    account_id=edge["node"]["account"]["id"],
                    is_payg=None,  # No longer supplied
                    is_blocked=None,  # No longer supplied
                    supplies=supplies,
                )
            )

        self._bootstrap_accounts = BootstrapAccounts(
            account_ids=[account.account_id for account in accounts],
            customer_id=json_response["data"]["customer_nextV1"]["id"],
            selected_account_id=accounts[
                0
            ].account_id,  # We no longer get this, so pick the first one, the user should specify otherwise
            is_first_login=False,  # We no longer get this, so assume false
            accounts=accounts,
        )

        return self._bootstrap_accounts

    async def get_daily_usage(
        self,
        date: str,
    ) -> OVODailyUsage:
        """Get daily usage data."""
        ovo_usage = OVODailyUsage(
            electricity=None,
            gas=None,
        )

        response = await self._request(
            f"{USAGE_DAILY_URL}/{self.account_id}?date={date}",
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
                                interval=(
                                    OVOInterval(
                                        start=datetime.fromisoformat(
                                            usage["interval"]["start"]
                                        ),
                                        end=datetime.fromisoformat(
                                            usage["interval"]["end"]
                                        ),
                                    )
                                    if "interval" in usage
                                    else None
                                ),
                                meter_readings=(
                                    OVOMeterReadings(
                                        start=usage["meterReadings"]["start"],
                                        end=usage["meterReadings"]["end"],
                                    )
                                    if "meterReadings" in usage
                                    else None
                                ),
                                has_half_hour_data=usage.get("hasHalfHourData", None),
                                cost=(
                                    OVOCost(
                                        amount=usage["cost"]["amount"],
                                        currency_unit=usage["cost"]["currencyUnit"],
                                    )
                                    if "cost" in usage
                                    else None
                                ),
                                rates=OVORates(
                                    anytime=usage["rates"].get("anytime", None),
                                    standing=usage["rates"].get("standing", None),
                                )
                                if "rates" in usage
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
                                interval=(
                                    OVOInterval(
                                        start=datetime.fromisoformat(
                                            usage["interval"]["start"]
                                        ),
                                        end=datetime.fromisoformat(
                                            usage["interval"]["end"]
                                        ),
                                    )
                                    if "interval" in usage
                                    else None
                                ),
                                meter_readings=(
                                    OVOMeterReadings(
                                        start=usage["meterReadings"]["start"],
                                        end=usage["meterReadings"]["end"],
                                    )
                                    if "meterReadings" in usage
                                    else None
                                ),
                                has_half_hour_data=usage.get("hasHalfHourData", None),
                                cost=OVOCost(
                                    amount=usage["cost"]["amount"],
                                    currency_unit=usage["cost"]["currencyUnit"],
                                )
                                if "cost" in usage
                                else None,
                                rates=OVORates(
                                    anytime=usage["rates"].get("anytime", None),
                                    standing=usage["rates"].get("standing", None),
                                )
                                if "rates" in usage
                                else None,
                            )
                        )

        return ovo_usage

    async def get_half_hourly_usage(
        self,
        date: str,
    ) -> OVOHalfHourUsage:
        """Get half hourly usage data."""
        ovo_usage = OVOHalfHourUsage(
            electricity=None,
            gas=None,
        )

        response = await self._request(
            f"{USAGE_HALF_HOURLY_URL}/{self.account_id}?date={date}",
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

    async def get_footprint(self) -> OVOFootprint:
        """Get footprint."""
        response = await self._request(
            f"{CARBON_FOOTPRINT_URL}/{self.account_id}/footprint",
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
            CARBON_INTENSITY_URL,
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
