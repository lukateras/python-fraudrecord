"""
Blocking FraudRecord query API client.
"""

from urllib.request import urlopen

from fraudrecord.model import APICode, QueryResponse, query_url


def query(api_code: APICode, **data_vars: str) -> QueryResponse:
    """
    Makes a query request to the API and returns a `QueryResponse`.
    """
    with urlopen(query_url(api_code, **data_vars)) as f:
        return QueryResponse.parse(f.read().decode("utf-8"))
