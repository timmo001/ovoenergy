"""Enable CLI."""
import asyncio

import click

from ovoenergy.ovoenergy import OVOEnergy


@click.command()
@click.option("--username", "-u", help="Username")
@click.option("--password", "-p", help="Password")
@click.option("--account", "-a", help="Account Number")
@click.option("--date", "-D", help="Date")
@click.option("--daily", "-d", is_flag=True, help="Daily usage")
@click.option("--halfhour", "-h", is_flag=True, help="Half hourly usage")
def cli(username, password, account, date, daily=True, halfhour=False):
    """CLI for this package."""
    asyncio.run(handle(username, password, account, date, daily, halfhour))


async def handle(username, password, account, date, daily=True, halfhour=False) -> None:
    client = OVOEnergy()
    authenticated = await client.authenticate(username, password, account)
    print(f"Authenticated: {authenticated}")
    if authenticated:
        print("Authenticated.")
        if daily is True:
            usage = await client.get_daily_usage(date)
            if usage is not None:
                print("Usage:")
                print(usage)
                if usage.electricity is not None:
                    print("Electricity:")
                    count = 0
                    for x in usage.electricity:
                        count += 1
                        print(f"{count}.consumption: {x.consumption}")
                        print(f"{count}.interval.start: {x.interval.start}")
                        print(f"{count}.interval.end: {x.interval.end}")
                        # print(f"{count}.meter_readings.start: {x.meter_readings.start}")
                        # print(f"{count}.meter_readings.end: {x.meter_readings.end}")
                        print(f"{count}.has_hh_data: {x.has_half_hour_data}")
                        print(f"{count}.cost.amount: {x.cost.amount}")
                        print(f"{count}.cost.currency_unit: {x.cost.currency_unit}")
                if usage.gas is not None:
                    print("Gas:")
                    count = 0
                    for x in usage.gas:
                        count += 1
                        print(f"{count}.consumption: {x.consumption}")
                        print(f"{count}.volume: {x.volume}")
                        print(f"{count}.interval.start: {x.interval.start}")
                        print(f"{count}.interval.end: {x.interval.end}")
                        # print(f"{count}.meter_readings.start: {x.meter_readings.start}")
                        # print(f"{count}.meter_readings.end: {x.meter_readings.end}")
                        print(f"{count}.has_hh_data: {x.has_half_hour_data}")
                        print(f"{count}.cost.amount: {x.cost.amount}")
                        print(f"{count}.cost.currency_unit: {x.cost.currency_unit}")
        if halfhour is True:
            usage = await client.get_half_hourly_usage(date)
            if usage is not None:
                print("Usage:")
                print(usage)
                if usage.electricity is not None:
                    print("Electricity:")
                    count = 0
                    for x in usage.electricity:
                        count += 1
                        print(f"consumption: {x.consumption}")
                        print(f"{count}.interval.start: {x.interval.start}")
                        print(f"{count}.interval.end: {x.interval.end}")
                        print(f"{count}.unit: {x.unit}")
                if usage.gas is not None:
                    print("Gas:")
                    count = 0
                    for x in usage.gas:
                        count += 1
                        print(f"{count}.consumption: {x.consumption}")
                        print(f"{count}.interval.start: {x.interval.start}")
                        print(f"{count}.interval.end: {x.interval.end}")
                        print(f"{count}.unit: {x.unit}")


cli()  # pylint: disable=E1120
