"""Fixtures for testing."""

from collections.abc import AsyncGenerator

from aiohttp import ClientSession
from aioresponses import aioresponses
import pytest

from ovoenergy import OVOEnergy

from . import (
    RESPONSE_JSON_AUTH,
    RESPONSE_JSON_BOOTSTRAP_ACCOUNTS,
    RESPONSE_JSON_DAILY_USAGE,
    RESPONSE_JSON_PLANS,
    RESPONSE_JSON_TOKEN,
)


@pytest.fixture(autouse=True)
def mock_aioresponse():
    """Return a client session."""
    with aioresponses() as mocker:
        mocker.post(
            "https://my.ovoenergy.com/api/v2/auth/login",
            payload=RESPONSE_JSON_AUTH,
            status=200,
            repeat=True,
        )
        mocker.get(
            "https://my.ovoenergy.com/api/v2/auth/token",
            payload=RESPONSE_JSON_TOKEN,
            status=200,
            repeat=True,
        )
        mocker.get(
            "https://smartpaymapi.ovoenergy.com/first-login/api/bootstrap/v2/",
            payload=RESPONSE_JSON_BOOTSTRAP_ACCOUNTS,
            status=200,
            repeat=True,
        )
        mocker.get(
            f"https://smartpaymapi.ovoenergy.com/usage/api/daily/{RESPONSE_JSON_BOOTSTRAP_ACCOUNTS['selectedAccountId']}?date=2024-01",
            payload=RESPONSE_JSON_DAILY_USAGE,
            status=200,
            repeat=True,
        )
        mocker.get(
            f"https://smartpaymapi.ovoenergy.com/usage/api/half-hourly/{RESPONSE_JSON_BOOTSTRAP_ACCOUNTS['selectedAccountId']}?date=2024-01-01",
            payload=RESPONSE_JSON_DAILY_USAGE,
            status=200,
            repeat=True,
        )
        mocker.get(
            f"https://smartpaymapi.ovoenergy.com/orex/api/plans/{RESPONSE_JSON_BOOTSTRAP_ACCOUNTS['selectedAccountId']}",
            payload=RESPONSE_JSON_PLANS,
            status=200,
            repeat=True,
        )

        yield mocker


@pytest.fixture
async def ovoenergy_client() -> AsyncGenerator[OVOEnergy, None]:
    """Return a OVOEnergy client."""
    async with ClientSession() as session:
        yield OVOEnergy(client_session=session)
