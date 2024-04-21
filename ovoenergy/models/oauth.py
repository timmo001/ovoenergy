"""OAuth model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class OAuth:
    """OAuth model."""

    access_token: str
    expires_in: int
    refresh_expires_in: int
    expires_at: datetime
