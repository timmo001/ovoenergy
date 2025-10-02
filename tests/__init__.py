"""Setup for tests."""

from typing import Final

USERNAME: Final[str] = "test"
PASSWORD: Final[str] = "test"
ACCOUNT: Final[int] = 123456789
ACCOUNT_BAD: Final[int] = 654321789

RESPONSE_JSON_BASIC: Final[dict] = {"test": "test"}

RESPONSE_JSON_AUTH: Final[dict] = {"code": "test"}

RESPONSE_JSON_TOKEN: Final[dict] = {
    "accessToken": {
        "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Y2FmZTljNC1hOTQyLTQ2YjUtYTY3Yy01ODgyZWJhMGEwM2MiLCJwZXJtaXNzaW9ucyI6WyJhY2NvdW50OjoxMjM0NTY3ODkiXSwiaWF0IjoxNjQwOTk1MjAwLCJleHAiOjE2NDA5OTg4MDB9.ZXZcYyG6vT0NMdKlUy9KDnCj4DJyC7o3rX_AmPef6hw"
    },
    "expiresIn": 3600,
    "refreshExpiresIn": 0,
}

RESPONSE_JSON_BOOTSTRAP_ACCOUNTS: Final[dict] = {
    "data": {
        "customer_nextV1": {
            "id": "5cafe9c4-a942-46b5-a67c-5882eba0a03c",
            "customerAccountRelationships": {
                "edges": [
                    {
                        "node": {
                            "account": {
                                "id": ACCOUNT,
                                "accountNo": str(ACCOUNT),
                                "accountSupplyPoints": [
                                    {
                                        "startDate": "2024-01-01T23:00:00Z",
                                        "supplyPoint": {
                                            "sprn": "3456766576",
                                            "fuelType": "gas",
                                            "isOnboarding": False,
                                            "isPayg": False,
                                            "address": {
                                                "addressLines": ["ADDR"],
                                                "postCode": "SW1A 1AA",
                                            },
                                            "meterTechnicalDetails": [
                                                {
                                                    "meterSerialNumber": "3456766576",
                                                    "mode": "credit",
                                                    "type": "AB123",
                                                    "status": "active",
                                                }
                                            ],
                                        },
                                    },
                                    {
                                        "startDate": "2024-01-01T23:00:00Z",
                                        "supplyPoint": {
                                            "sprn": "4536756746",
                                            "fuelType": "electricity",
                                            "isOnboarding": False,
                                            "isPayg": False,
                                            "address": {
                                                "addressLines": ["ADDR"],
                                                "postCode": "SW1A 1AA",
                                            },
                                            "meterTechnicalDetails": [
                                                {
                                                    "meterSerialNumber": "4536756746",
                                                    "mode": "credit",
                                                    "type": "AB123",
                                                    "status": "active",
                                                }
                                            ],
                                        },
                                    },
                                ],
                            },
                        },
                    }
                ],
            },
        },
    },
}

RESPONSE_JSON_DAILY_USAGE: Final[dict] = {
    "electricity": {
        "data": [
            {
                "consumption": 10.24,
                "interval": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-01T23:59:59.999000Z",
                },
                "meterReadings": {
                    "start": "12345",
                    "end": "67890",
                },
                "hasHalfHourData": None,
                "cost": {"amount": "2.94", "currencyUnit": "GBP"},
                "rates": {
                    "anytime": 0.25,
                    "standing": 0.45,
                },
            }
        ],
    },
    "gas": {
        "data": [
            {
                "consumption": 14.68,
                "volume": None,
                "interval": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-01T23:59:59.999000Z",
                },
                "meterReadings": {
                    "start": "12345",
                    "end": "67890",
                },
                "hasHalfHourData": None,
                "cost": {"amount": "2.56", "currencyUnit": "GBP"},
                "rates": {
                    "anytime": 0.18,
                    "standing": 0.35,
                },
            }
        ],
    },
}

RESPONSE_JSON_HALF_HOURLY_USAGE: Final[dict] = {
    "electricity": {
        "data": [
            {
                "consumption": 0.5,
                "interval": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-01T00:30:00Z",
                },
                "unit": "kWh",
            }
        ],
    },
    "gas": {
        "data": [
            {
                "consumption": 0.2,
                "interval": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-01T00:30:00Z",
                },
                "unit": "m³",
            }
        ],
    },
}

RESPONSE_JSON_FOOTPRINT: Final[dict] = {
    "from": "2024-01-01T00:00:00Z",
    "to": "2024-01-01T23:59:59.999000Z",
    "carbonReductionProductIds": [],
    "carbonFootprint": {
        "carbonKg": 2200.1234,
        "carbonSavedKg": 0.0,
        "kWh": 1578.3246,
        "breakdown": {
            "electricity": {
                "carbonKg": 200.1234,
                "carbonSavedKg": 230.02,
                "kWh": 65645.92,
            },
            "gas": {
                "carbonKg": 2000.1234,
                "carbonSavedKg": 340.02,
                "kWh": 10664.74363579,
            },
        },
    },
}

RESPONSE_JSON_INTENSITY: Final[dict] = {
    "forecast": [
        {
            "from": "2pm",
            "intensity": 82,
            "level": "low",
            "colour": "#0A9928",
            "colourV2": "#0D8426",
        },
    ],
    "current": "low",
    "greentime": None,
}
