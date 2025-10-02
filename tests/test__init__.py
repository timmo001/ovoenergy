"""Tests for the client module."""

from datetime import datetime, timedelta

from aioresponses import aioresponses
import pytest
from syrupy.assertion import SnapshotAssertion

from ovoenergy import OVOEnergy
from ovoenergy.const import AUTH_LOGIN_URL, AUTH_TOKEN_URL, USAGE_DAILY_URL
from ovoenergy.exceptions import (
    OVOEnergyAPINoCookies,
    OVOEnergyAPINotAuthorized,
    OVOEnergyAPINotFound,
    OVOEnergyNoAccount,
)

from . import ACCOUNT, ACCOUNT_BAD, PASSWORD, RESPONSE_JSON_AUTH, USERNAME


@pytest.mark.asyncio
async def test_authorize(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test authorize."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    assert not ovoenergy_client.oauth_expired

    assert ovoenergy_client.oauth is not None

    assert ovoenergy_client.oauth.access_token == snapshot(
        name="authorize_oauth_access_token",
    )
    assert ovoenergy_client.oauth.expires_in == snapshot(
        name="authorize_oauth_expires_in",
    )
    assert ovoenergy_client.oauth.refresh_expires_in == snapshot(
        name="authorize_oauth_refresh_expires_in",
    )
    assert ovoenergy_client.account_id == snapshot(
        name="authorize_account_id",
    )
    assert ovoenergy_client.account_ids == snapshot(
        name="authorize_account_ids",
    )
    assert ovoenergy_client.customer_id == snapshot(
        name="authorize_customer_id",
    )
    assert ovoenergy_client.username == snapshot(
        name="authorize_username",
    )


@pytest.mark.asyncio
async def test_bootstrap(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test bootstrap."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    assert await ovoenergy_client.bootstrap_accounts() == snapshot(
        name="bootstrap_accounts",
    )


@pytest.mark.asyncio
async def test_get_daily_usage(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get daily usage."""
    with pytest.raises(OVOEnergyNoAccount):
        await ovoenergy_client.get_daily_usage("2024-01")

    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    assert await ovoenergy_client.get_daily_usage("2024-01") == snapshot(
        name="daily_usage",
    )


@pytest.mark.asyncio
async def test_get_half_hourly_usage(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get half hourly usage."""
    with pytest.raises(OVOEnergyNoAccount):
        await ovoenergy_client.get_half_hourly_usage("2024-01-01")

    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    assert await ovoenergy_client.get_half_hourly_usage("2024-01-01") == snapshot(
        name="half_hourly_usage",
    )


@pytest.mark.asyncio
async def test_get_footprint(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get footprint."""
    with pytest.raises(OVOEnergyNoAccount):
        await ovoenergy_client.get_footprint()

    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    assert await ovoenergy_client.get_footprint() == snapshot(
        name="footprint",
    )


@pytest.mark.asyncio
async def test_get_carbon_intensity(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get carbon intensity."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    assert await ovoenergy_client.get_carbon_intensity() == snapshot(
        name="carbon_intensity",
    )


@pytest.mark.asyncio
async def test_bootstrap_custom_account(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test bootstrap custom account."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    ovoenergy_client.custom_account_id = ACCOUNT

    await ovoenergy_client.bootstrap_accounts()

    assert await ovoenergy_client.get_daily_usage("2024-01") == snapshot(
        name="bootstrap_accounts_custom_account",
    )


@pytest.mark.asyncio
async def test_bad_account(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test bad account."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    ovoenergy_client.custom_account_id = ACCOUNT_BAD

    with pytest.raises(OVOEnergyAPINotFound):
        await ovoenergy_client.get_daily_usage("2024-01")


# pylint: disable=protected-access
@pytest.mark.asyncio
async def test_no_cookies(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test no cookies."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    ovoenergy_client._cookies = None

    with pytest.raises(OVOEnergyAPINoCookies):
        await ovoenergy_client.get_daily_usage("2024-01")


# pylint: disable=protected-access
@pytest.mark.asyncio
async def test_no_auth(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test no auth."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    ovoenergy_client._oauth = None

    with pytest.raises(OVOEnergyAPINotAuthorized):
        await ovoenergy_client.get_daily_usage("2024-01")


# pylint: disable=protected-access
@pytest.mark.asyncio
async def test_oauth_expired(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test oauth expired."""
    an_hour_ago = datetime.now() - timedelta(hours=1)

    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    assert ovoenergy_client._oauth is not None

    ovoenergy_client._oauth.expires_at = an_hour_ago

    await ovoenergy_client.get_daily_usage("2024-01")

    ovoenergy_client._oauth.expires_at = an_hour_ago

    mock_aioresponse.clear()
    mock_aioresponse.get(
        AUTH_TOKEN_URL,
        status=403,
        repeat=True,
    )

    with pytest.raises(OVOEnergyAPINotAuthorized):
        await ovoenergy_client.get_daily_usage("2024-01")


@pytest.mark.asyncio
async def test_forbidden(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test forbidden."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    mock_aioresponse.clear()
    mock_aioresponse.get(
        f"{USAGE_DAILY_URL}/{ACCOUNT}?date=2024-01",
        status=403,
        repeat=True,
    )

    with pytest.raises(OVOEnergyAPINotAuthorized):
        await ovoenergy_client.get_daily_usage("2024-01")


@pytest.mark.asyncio
async def test_auth_not_found(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test auth endpoint not found."""
    mock_aioresponse.clear()
    mock_aioresponse.post(
        AUTH_LOGIN_URL,
        status=404,
        repeat=True,
    )

    with pytest.raises(OVOEnergyAPINotFound):
        await ovoenergy_client.authenticate(USERNAME, PASSWORD)


@pytest.mark.asyncio
async def test_auth_code_not_found(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test auth endpoint code not found."""
    mock_aioresponse.clear()
    mock_aioresponse.post(
        AUTH_LOGIN_URL,
        status=204,
        repeat=True,
    )

    assert not await ovoenergy_client.authenticate(USERNAME, PASSWORD)


@pytest.mark.asyncio
async def test_auth_code_unknown(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test auth token not found."""
    mock_aioresponse.clear()
    mock_aioresponse.post(
        AUTH_LOGIN_URL,
        status=200,
        payload={"code": "Unknown"},
        repeat=True,
    )

    assert not await ovoenergy_client.authenticate(USERNAME, PASSWORD)


@pytest.mark.asyncio
async def test_auth_token_not_found(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
) -> None:
    """Test auth token not found."""
    mock_aioresponse.clear()
    mock_aioresponse.post(
        AUTH_LOGIN_URL,
        payload=RESPONSE_JSON_AUTH,
        status=200,
        repeat=True,
    )
    mock_aioresponse.get(
        AUTH_TOKEN_URL,
        status=404,
        repeat=True,
    )

    with pytest.raises(OVOEnergyAPINotFound):
        await ovoenergy_client.authenticate(USERNAME, PASSWORD)
