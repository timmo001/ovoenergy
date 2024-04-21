"""Exceptions for the OVO Energy API."""


# Base Exceptions
class OVOEnergyException(Exception):
    """Base exception for OVO Energy."""


class OVOEnergyNoAccount(OVOEnergyException):
    """Exception for no account found."""


# API Exceptions
class OVOEnergyAPIException(OVOEnergyException):
    """Exception for API exceptions."""


class OVOEnergyAPINotAuthorized(OVOEnergyAPIException):
    """Exception for API client not authorized."""


class OVOEnergyAPINoCookies(OVOEnergyAPIException):
    """Exception for no cookies found."""
