"""Setup for tests."""

from typing import Final

USERNAME: Final[str] = "test"
PASSWORD: Final[str] = "test"
ACCOUNT: Final[int] = 123456789
ACCOUNT_BAD: Final[int] = 654321789

RESPONSE_JSON_BASIC: Final[dict] = {"test": "test"}

RESPONSE_JSON_AUTH: Final[dict] = {"code": "test"}

RESPONSE_JSON_TOKEN: Final[dict] = {
    "accessToken": {"value": "test"},
    "expiresIn": 3600,
    "refreshExpiresIn": 0,
}

RESPONSE_JSON_BOOTSTRAP_ACCOUNTS: Final[dict] = {
    "accountIds": [ACCOUNT],
    "customerId": "5cafe9c4-a942-46b5-a67c-5882eba0a03c",
    "selectedAccountId": ACCOUNT,
    "accounts": [
        {
            "accountId": ACCOUNT,
            "isPayg": False,
            "isBlocked": False,
            "supplies": [
                {
                    "mpxn": "3456766576",
                    "fuel": "gas",
                    "isOnboarding": False,
                    "start": "2024-01-01T23:00:00Z",
                    "isPayg": False,
                    "supplyPointInfo": {
                        "meterType": "AB123",
                        "meterNotFound": False,
                        "address": ["ADDR"],
                    },
                },
                {
                    "mpxn": "4536756746",
                    "fuel": "electricity",
                    "isOnboarding": False,
                    "start": "2024-01-01T23:00:00Z",
                    "isPayg": False,
                    "supplyPointInfo": {
                        "meterType": "AB123",
                        "meterNotFound": False,
                        "address": ["ADDR"],
                    },
                },
            ],
        }
    ],
    "isFirstLogin": False,
}

RESPONSE_JSON_DAILY_USAGE: Final[dict] = {
    "electricity": [
        {
            "consumption": 10.24,
            "interval": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-01T23:59:59.999000Z",
            },
            "meterReadings": None,
            "hasHalfHourData": None,
            "cost": {"amount": "2.94", "currencyUnit": "GBP"},
        }
    ],
    "gas": [
        {
            "consumption": 14.68,
            "volume": None,
            "interval": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-01T23:59:59.999000Z",
            },
            "meterReadings": None,
            "hasHalfHourData": None,
            "cost": {"amount": "2.56", "currencyUnit": "GBP"},
        },
    ],
}

RESPONSE_JSON_PLANS: Final[dict] = {
    "electricity": [],
    "gas": [],
}
