"""OVO Energy: Main"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Optional

import typer

from ._version import __version__
from .models import OVODailyUsage, OVOHalfHourUsage
from .models.plan import OVOPlan
from .ovoenergy import OVOEnergy

app = typer.Typer()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@app.command(name="daily", short_help="Get daily usage from OVO Energy")
def daily(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: str = typer.Option(None, help="OVO Energy account number"),
    date: str = typer.Option(None, help="Date to retrieve data for"),
) -> None:
    """Get daily usage from OVO Energy."""
    if date is None:
        # Get this month
        date = datetime.now().strftime("%Y-%m")

    ovo_usage: Optional[OVODailyUsage] = None

    client = OVOEnergy()

    authenticated = loop.run_until_complete(
        client.authenticate(username, password, account)
    )
    if authenticated:
        ovo_usage = loop.run_until_complete(client.get_daily_usage(date))

    typer.secho(
        ovo_usage.json() if ovo_usage is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )


@app.command(name="halfhourly", short_help="Get half hourly usage from OVO Energy")
def half_hourly(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: str = typer.Option(None, help="OVO Energy account number"),
    date: str = typer.Option(None, help="Date to retrieve data for"),
) -> None:
    """Get half hourly usage from OVO Energy."""
    if date is None:
        # Get yesterday's date
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    ovo_usage: Optional[OVOHalfHourUsage] = None

    client = OVOEnergy()
    authenticated = loop.run_until_complete(
        client.authenticate(username, password, account)
    )
    if authenticated:
        ovo_usage = loop.run_until_complete(client.get_half_hourly_usage(date))

    typer.secho(
        ovo_usage.json() if ovo_usage is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )


@app.command(name="plan", short_help="Get plan from OVO Energy")
def plan(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: str = typer.Option(None, help="OVO Energy account number"),
) -> None:
    """Get rates from OVO Energy."""
    ovo_plan: Optional[OVOPlan] = None

    client = OVOEnergy()
    authenticated = loop.run_until_complete(
        client.authenticate(username, password, account)
    )
    if authenticated:
        ovo_plan = loop.run_until_complete(client.get_plan())

    typer.secho(
        ovo_plan.json() if ovo_plan is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )


@app.command(name="version", short_help="Module Version")
def version() -> None:
    """Module Version"""
    typer.secho(__version__.public(), fg=typer.colors.CYAN)


if __name__ == "__main__":
    app()
