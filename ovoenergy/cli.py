"""Enable CLI."""
import json
import click


@click.command()
@click.option("--username", "-u", help="Username")
@click.option("--password", "-p", help="Password")
@click.option("--date", "-d", help="Date")
@click.option("--daily", "-d", is_flag=True, help="Daily usage")
@click.option("--halfhour", "-h", is_flag=True, help="Half hourly usage")
def cli(username, password, date, daily=True, halfhour=False):
    """CLI for this package."""
    from ovoenergy.ovoenergy import OVOEnergy
    ovo = OVOEnergy(username, password)
    if daily is True:
        print(json.dumps(ovo.get_daily_usage(date)))
    if daily is True:
        print(json.dumps(ovo.get_half_hourly_usage(date)))


cli()  # pylint: disable=E1120
