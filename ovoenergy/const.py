"""Constants for the OVO Energy API client."""

# Base URLs
AUTH_BASE_URL = "https://my.ovoenergy.com/api/v2/auth"
SMARTPAY_BASE_URL = "https://smartpaymapi.ovoenergy.com"
KALUZA_BASE_URL = "https://api.eu1.prod.kaluza.com"

# Authentication endpoints
AUTH_LOGIN_URL = f"{AUTH_BASE_URL}/login"
AUTH_TOKEN_URL = f"{AUTH_BASE_URL}/token"

# Bootstrap endpoints
BOOTSTRAP_GRAPHQL_URL = f"{KALUZA_BASE_URL}/graphql/1"

# Usage endpoints
USAGE_DAILY_URL = f"{SMARTPAY_BASE_URL}/usage/api/daily"
USAGE_HALF_HOURLY_URL = f"{SMARTPAY_BASE_URL}/usage/api/half-hourly"


# Carbon endpoints
CARBON_FOOTPRINT_URL = f"{SMARTPAY_BASE_URL}/carbon-api"
CARBON_INTENSITY_URL = f"{SMARTPAY_BASE_URL}/carbon-bff/carbonintensity"

# GraphQL query for bootstrapping customer accounts
BOOTSTRAP_QUERY = """
query Bootstrap($customerId: ID!) {
  customer_nextV1(id: $customerId) {
    id
    customerAccountRelationships {
      edges {
        node {
          account {
            accountNo
            id
            accountSupplyPoints {
              ...AccountSupplyPoint
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment AccountSupplyPoint on AccountSupplyPoint {
  startDate
  supplyPoint {
    sprn
    fuelType
    meterTechnicalDetails {
      meterSerialNumber
      mode
      type
      status
      __typename
    }
    address {
      addressLines
      postCode
      __typename
    }
    __typename
  }
  __typename
}
"""
