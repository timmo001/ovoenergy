"""Test __version__ module."""

from aioazuredevops._version import __version__


def test__version():
    """Test the __version__ string."""
    assert isinstance(__version__.public(), str)
