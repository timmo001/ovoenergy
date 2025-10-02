"""Main."""

import asyncio
from dataclasses import asdict
from datetime import datetime, timedelta
import os
from pathlib import Path

import aiohttp
import typer

from . import OVOEnergy


def _load_env_file(env_path: str = ".env") -> None:
    """Load environment variables from .env file."""
    env_file = Path(env_path)
    if not env_file.exists():
        return

    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Split on first = sign
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value


# Load environment variables from .env file
_load_env_file()

app = typer.Typer()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def _setup_client(
    account: int | None = None,
) -> tuple[OVOEnergy, aiohttp.ClientSession]:
    """Set up OVO Energy client."""
    # Get credentials from environment variables
    username = os.getenv("OVO_USERNAME")
    password = os.getenv("OVO_PASSWORD")

    if not username or not password:
        typer.secho(
            "Error: OVO_USERNAME and OVO_PASSWORD must be set in .env file",
            fg=typer.colors.RED,
        )
        raise typer.Abort()

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

    [client, client_session] = loop.run_until_complete(_setup_client(account))
    ovo_usage = loop.run_until_complete(client.get_daily_usage(date))

    typer.secho(
        asdict(ovo_usage) if ovo_usage is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="halfhourly", short_help="Get half hourly usage from OVO Energy")
def half_hourly(
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

    [client, client_session] = loop.run_until_complete(_setup_client(account))
    ovo_usage = loop.run_until_complete(client.get_half_hourly_usage(date))

    typer.secho(
        asdict(ovo_usage) if ovo_usage is not None else '{"message": "No data"}',
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="carbon-footprint", short_help="Get carbon footprint from OVO Energy")
def carbon_footprint(
    account: int = typer.Option(
        None, help="OVO Energy account number (default: first account)"
    ),
) -> None:
    """Get carbon footprint from OVO Energy."""
    [client, client_session] = loop.run_until_complete(_setup_client(account))
    ovo_footprint = loop.run_until_complete(client.get_footprint())

    typer.secho(
        (
            asdict(ovo_footprint)
            if ovo_footprint is not None
            else '{"message": "No data"}'
        ),
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


@app.command(name="carbon-intensity", short_help="Get carbon intensity from OVO Energy")
def carbon_intensity(
    account: int = typer.Option(
        None, help="OVO Energy account number (default: first account)"
    ),
) -> None:
    """Get carbon intensity from OVO Energy."""
    [client, client_session] = loop.run_until_complete(_setup_client(account))
    ovo_carbon_intensity = loop.run_until_complete(client.get_carbon_intensity())

    typer.secho(
        (
            asdict(ovo_carbon_intensity)
            if ovo_carbon_intensity is not None
            else '{"message": "No data"}'
        ),
        fg=typer.colors.GREEN,
    )
    loop.run_until_complete(client_session.close())


if __name__ == "__main__":
    app()
