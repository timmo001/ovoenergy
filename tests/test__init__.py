"""Tests for the client module."""

from aioresponses import aioresponses
import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import paths

from ovoenergy import OVOEnergy
from ovoenergy.exceptions import OVOEnergyNoAccount

from . import ACCOUNT, ACCOUNT_BAD, PASSWORD, USERNAME


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
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    assert await ovoenergy_client.get_half_hourly_usage("2024-01-01") == snapshot(
        name="half_hourly_usage",
    )


@pytest.mark.asyncio
async def test_get_plans(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get plans."""
    await ovoenergy_client.authenticate(USERNAME, PASSWORD)

    await ovoenergy_client.bootstrap_accounts()

    assert await ovoenergy_client.get_plans() == snapshot(
        name="plans",
    )


@pytest.mark.asyncio
async def test_get_footprint(
    ovoenergy_client: OVOEnergy,
    mock_aioresponse: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test get footprint."""
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


# @pytest.mark.asyncio
# async def test_bootstrap_custom_account(
#     ovoenergy_client: OVOEnergy,
#     mock_aioresponse: aioresponses,
#     snapshot: SnapshotAssertion,
# ) -> None:
#     """Test get_daily_usage."""
#     await ovoenergy_client.authenticate(USERNAME, PASSWORD)

#     ovoenergy_client.custom_account_id = ACCOUNT

#     await ovoenergy_client.bootstrap_accounts()

#     assert await ovoenergy_client.get_daily_usage("2024-01") == snapshot(
#         name="bootstrap_accounts_custom_account",
#     )


# @pytest.mark.asyncio
# async def test_account_bad(
#     ovoenergy_client: OVOEnergy,
#     mock_aioresponse: aioresponses,
#     snapshot: SnapshotAssertion,
# ) -> None:
#     """Test get_daily_usage."""
#     ovoenergy_client.custom_account_id = ACCOUNT_BAD

#     with pytest.raises(OVOEnergyNoAccount):
#         await ovoenergy_client.authenticate(USERNAME, PASSWORD)

#     with pytest.raises(OVOEnergyNoAccount):
#         await ovoenergy_client.bootstrap_accounts()
