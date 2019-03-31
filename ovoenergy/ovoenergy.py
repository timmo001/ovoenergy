"""Get energy data from OVO's API."""
import sys
import json
import requests


class OVOEnergy():
    """Class for OVOEnergy."""

    def __init__(self, username, password):
        """Initilalize."""
        try:
            response = requests.post(
                'https://my.ovoenergy.com/api/v2/auth/login',
                json={"username": username,
                      "password": password,
                      "rememberMe": True})
            json_response = response.json()
            if 'code' in json_response and json_response['code'] == 'Unknown':
                print(json.dumps(json_response))
                sys.exit(1)
            else:
                self.cookies = response.cookies
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get_daily_usage(self, month):
        """Get daily usage data."""
        if month is None:
            return None
        electricity_usage = None
        gas_usage = None
        try:
            response = requests.get(
                'https://smartpaym.ovoenergy.com/api/energy-usage/daily/6129307?date=' + month,
                cookies=self.cookies)
            json_response = response.json()
            if 'electricity' in json_response:
                electricity = json_response['electricity']
                if 'data' in electricity:
                    electricity_usage = electricity['data']
            if 'gas' in json_response:
                gas = json_response['gas']
                if 'data' in gas:
                    gas_usage = gas['data']
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        return {'electricity': electricity_usage, 'gas': gas_usage}

    def get_half_hourly_usage(self, date):
        """Get half hourly usage data."""
        if date is None:
            return None
        electricity_usage = None
        gas_usage = None
        try:
            response = requests.get(
                'https://smartpaym.ovoenergy.com/api/energy-usage/half-hourly/6129307?date=' + date,
                cookies=self.cookies)
            json_response = response.json()
            if 'electricity' in json_response:
                electricity = json_response['electricity']
                if 'data' in electricity:
                    electricity_usage = electricity['data']
            if 'gas' in json_response:
                gas = json_response['gas']
                if 'data' in gas:
                    gas_usage = gas['data']
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        return {'electricity': electricity_usage, 'gas': gas_usage}
