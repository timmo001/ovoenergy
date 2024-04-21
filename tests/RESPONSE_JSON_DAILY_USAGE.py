from typing import Final

RESPONSE_JSON_DAILY_USAGE: Final[dict] = {
    "electricity": [
        {
            "consumption": 17.42,
            "interval": {
                "start": datetime.datetime(2024, 4, 1, 0, 0),
                "end": datetime.datetime(2024, 4, 1, 23, 59, 59, 999000),
            },
            "meter_readings": None,
            "has_half_hour_data": None,
            "cost": {"amount": "3.94", "currency_unit": "GBP"},
        }
    ],
    "gas": [
        {
            "consumption": 32.44,
            "volume": None,
            "interval": {
                "start": datetime.datetime(2024, 4, 1, 0, 0),
                "end": datetime.datetime(2024, 4, 1, 23, 59, 59, 999000),
            },
            "meter_readings": None,
            "has_half_hour_data": None,
            "cost": {"amount": "1.82", "currency_unit": "GBP"},
        },

    ],
}
