"""Constants for the OVO Energy API client."""

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
