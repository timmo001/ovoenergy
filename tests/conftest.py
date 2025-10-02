"""Fixtures for testing."""

from collections.abc import AsyncGenerator

from aiohttp import ClientSession
from aioresponses import aioresponses
import pytest

from ovoenergy import OVOEnergy
from ovoenergy.const import (
    AUTH_LOGIN_URL,
    AUTH_TOKEN_URL,
    BOOTSTRAP_GRAPHQL_URL,
    CARBON_FOOTPRINT_URL,
    CARBON_INTENSITY_URL,
    USAGE_DAILY_URL,
    USAGE_HALF_HOURLY_URL,
)

from . import (
    ACCOUNT,
    RESPONSE_JSON_AUTH,
    RESPONSE_JSON_BOOTSTRAP_ACCOUNTS,
    RESPONSE_JSON_DAILY_USAGE,
    RESPONSE_JSON_FOOTPRINT,
    RESPONSE_JSON_INTENSITY,
    RESPONSE_JSON_TOKEN,
)


@pytest.fixture(autouse=True)
def mock_aioresponse():
    """Return a client session."""
    with aioresponses() as mocker:
        mocker.post(
            AUTH_LOGIN_URL,
            payload=RESPONSE_JSON_AUTH,
            status=200,
            repeat=True,
        )
        mocker.get(
            AUTH_TOKEN_URL,
            payload=RESPONSE_JSON_TOKEN,
            status=200,
            repeat=True,
        )
        mocker.get(
            BOOTSTRAP_GRAPHQL_URL,
            payload=RESPONSE_JSON_BOOTSTRAP_ACCOUNTS,
            status=200,
            repeat=True,
        )
        mocker.get(
            f"{USAGE_DAILY_URL}/{ACCOUNT}?date=2024-01",
            payload=RESPONSE_JSON_DAILY_USAGE,
            status=200,
            repeat=True,
        )
        mocker.get(
            f"{USAGE_HALF_HOURLY_URL}/{ACCOUNT}?date=2024-01-01",
            payload=RESPONSE_JSON_DAILY_USAGE,
            status=200,
            repeat=True,
        )
        mocker.get(
            f"{CARBON_FOOTPRINT_URL}/{ACCOUNT}/footprint",
            payload=RESPONSE_JSON_FOOTPRINT,
            status=200,
            repeat=True,
        )
        mocker.get(
            CARBON_INTENSITY_URL,
            payload=RESPONSE_JSON_INTENSITY,
            status=200,
            repeat=True,
        )

        yield mocker


@pytest.fixture
async def ovoenergy_client() -> AsyncGenerator[OVOEnergy, None]:
    """Return a OVOEnergy client."""
    async with ClientSession() as session:
        yield OVOEnergy(client_session=session)
