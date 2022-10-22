"""
Non-blocking FraudRecord query API client.

*Requires `aio` extra to be installed.*
"""

import aiohttp

from fraudrecord.model import APICode, QueryResponse, query_url


async def query(api_code: APICode, **data_vars: str) -> QueryResponse:
    """
    Makes a query request to the API and returns a `QueryResponse`.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(query_url(api_code, **data_vars)) as response:
            return QueryResponse.parse(await response.text())
