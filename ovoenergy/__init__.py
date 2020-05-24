"""Initialize the package."""
from datetime import datetime
from typing import List


class OvoInterval:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end


class OvoMeterReadings:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end


class OvoCost:
    def __init__(self, amount: float, currency_unit: str):
        self.amount = amount
        self.currency_unit = currency_unit


class OvoDailyElectricity:
    def __init__(
        self,
        consumption: float,
        interval: OvoInterval,
        meter_readings: OvoMeterReadings,
        has_half_hour_data: bool,
        cost: OvoCost,
    ):
        self.consumption = consumption
        self.interval = interval
        self.meter_readings = meter_readings
        self.has_half_hour_data = has_half_hour_data
        self.cost = cost


class OvoDailyGas:
    def __init__(
        self,
        consumption: float,
        volume: float,
        interval: OvoInterval,
        meter_readings: OvoMeterReadings,
        has_half_hour_data: bool,
        cost: OvoCost,
    ):
        self.consumption = consumption
        self.volume = volume
        self.interval = interval
        self.meter_readings = meter_readings
        self.has_half_hour_data = has_half_hour_data
        self.cost = cost


class OvoHalfHour:
    def __init__(self, consumption: float, interval: OvoInterval, unit: str):
        self.consumption = consumption
        self.interval = interval
        self.unit = unit


class OvoDailyUsage:
    def __init__(self, electricity: List[OvoDailyElectricity], gas: List[OvoDailyGas]):
        self.electricity = electricity
        self.gas = gas


class OvoHalfHourUsage:
    def __init__(self, electricity: List[OvoHalfHour], gas: List[OvoHalfHour]):
        self.electricity = electricity
        self.gas = gas
