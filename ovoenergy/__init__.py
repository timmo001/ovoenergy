"""Initialize the package."""
from datetime import datetime
from typing import List


class OVOInterval:
    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end


class OVOMeterReadings:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end


class OVOCost:
    def __init__(self, amount: float, currency_unit: str):
        self.amount = amount
        self.currency_unit = currency_unit


class OVODailyElectricity:
    def __init__(
        self,
        consumption: float,
        interval: OVOInterval,
        meter_readings: OVOMeterReadings,
        has_half_hour_data: bool,
        cost: OVOCost,
    ):
        self.consumption = consumption
        self.interval = interval
        self.meter_readings = meter_readings
        self.has_half_hour_data = has_half_hour_data
        self.cost = cost


class OVODailyGas:
    def __init__(
        self,
        consumption: float,
        volume: float,
        interval: OVOInterval,
        meter_readings: OVOMeterReadings,
        has_half_hour_data: bool,
        cost: OVOCost,
    ):
        self.consumption = consumption
        self.volume = volume
        self.interval = interval
        self.meter_readings = meter_readings
        self.has_half_hour_data = has_half_hour_data
        self.cost = cost


class OVOHalfHour:
    def __init__(self, consumption: float, interval: OVOInterval, unit: str):
        self.consumption = consumption
        self.interval = interval
        self.unit = unit


class OVODailyUsage:
    def __init__(self, electricity: List[OVODailyElectricity], gas: List[OVODailyGas]):
        self.electricity = electricity
        self.gas = gas


class OVOHalfHourUsage:
    def __init__(self, electricity: List[OVOHalfHour], gas: List[OVOHalfHour]):
        self.electricity = electricity
        self.gas = gas
