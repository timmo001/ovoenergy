"""Main."""

import asyncio
from datetime import datetime, timedelta

import aiohttp
import typer

from . import OVOEnergy
from ._version import __version__
from .models import OVODailyUsage, OVOHalfHourUsage
from .models.carbon_intensity import OVOCarbonIntensity
from .models.footprint import OVOFootprint
from .models.plan import OVOPlan

app = typer.Typer()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def _setup_client(
    username: str,
    password: str,
    account: int | None = None,
) -> tuple[OVOEnergy, aiohttp.ClientSession]:
    """Set up OVO Energy client."""
    client_session = aiohttp.ClientSession()
    client = OVOEnergy(
        client_session=client_session,
    )

    if not await client.authenticate(username, password):
        typer.secho("Authentication failed", fg=typer.colors.RED)
        raise typer.Abort()

    await client.bootstrap_accounts()

    if account is not None:
        client.custom_account_id = account

    return (client, client_session)


@app.command(name="daily", short_help="Get daily usage from OVO Energy")
def daily(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: int = typer.Option(
        None, help="OVO Energy account number (default: first account)"
    ),
    date: str = typer.Option(
        None, help="Date to retrieve data for (default: this month)"
    ),
) -> None:
    """Get daily usage from OVO Energy."""
    if date is None:
        # Get this month
        date = datetime.now().strftime("%Y-%m")

    ovo_usage: OVODailyUsage | None = None

    [client, client_session] = loop.run_until_complete(
        _setup_client(username, password, account)
    )
    ovo_usage = loop.run_until_complete(client.get_daily_usage(date))

    typer.secho(
        ovo_usage if ovo_usage is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="halfhourly", short_help="Get half hourly usage from OVO Energy")
def half_hourly(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: int = typer.Option(
        None, help="OVO Energy account number (default: first account)"
    ),
    date: str = typer.Option(
        None, help="Date to retrieve data for (default: this month)"
    ),
) -> None:
    """Get half hourly usage from OVO Energy."""
    if date is None:
        # Get yesterday's date
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    ovo_usage: OVOHalfHourUsage | None = None

    [client, client_session] = loop.run_until_complete(
        _setup_client(username, password, account)
    )
    ovo_usage = loop.run_until_complete(client.get_half_hourly_usage(date))

    typer.secho(
        ovo_usage if ovo_usage is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="plan", short_help="Get plan from OVO Energy")
def plan(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: int = typer.Option(
        None, help="OVO Energy account number (default: first account)"
    ),
) -> None:
    """Get rates from OVO Energy."""
    ovo_plan: OVOPlan | None = None

    [client, client_session] = loop.run_until_complete(
        _setup_client(username, password, account)
    )
    ovo_plan = loop.run_until_complete(client.get_plan())

    typer.secho(
        ovo_plan if ovo_plan is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="carbon-footprint", short_help="Get carbon footprint from OVO Energy")
def carbon_footprint(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: int = typer.Option(
        None, help="OVO Energy account number (default: first account)"
    ),
) -> None:
    """Get carbon footprint from OVO Energy."""
    ovo_footprint: OVOFootprint | None = None

    [client, client_session] = loop.run_until_complete(
        _setup_client(username, password, account)
    )
    ovo_footprint = loop.run_until_complete(client.get_footprint())

    typer.secho(
        ovo_footprint if ovo_footprint is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="carbon-intensity", short_help="Get carbon intensity from OVO Energy")
def carbon_intensity(
    username: str = typer.Option(..., help="OVO Energy username"),
    password: str = typer.Option(..., help="OVO Energy password"),
    account: int = typer.Option(
        None, help="OVO Energy account number (default: first account)"
    ),
) -> None:
    """Get carbon intensity from OVO Energy."""
    ovo_carbon_intensity: OVOCarbonIntensity | None = None

    [client, client_session] = loop.run_until_complete(
        _setup_client(username, password, account)
    )
    ovo_carbon_intensity = loop.run_until_complete(client.get_carbon_intensity())

    typer.secho(
        ovo_carbon_intensity
        if ovo_carbon_intensity is not None
        else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="version", short_help="Module Version")
def version() -> None:
    """Display module version."""
    typer.secho(__version__.public(), fg=typer.colors.CYAN)


if __name__ == "__main__":
    app()
