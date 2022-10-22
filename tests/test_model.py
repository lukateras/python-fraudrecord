from decimal import Decimal
from urllib.parse import parse_qs, urlparse

from pydantic import ValidationError
from pytest import raises

from fraudrecord.hash import hexdigest
from fraudrecord.model import QueryResponse, query_url, report_url


def test_query_url():
    api_code = "1dc2d4745dccc866"
    email = "example@example.org"
    params = {
        "_action": ["query"],
        "_api": [api_code],
        "email": [hexdigest(email)],
    }

    url = query_url(api_code, email=email)
    assert parse_qs(urlparse(url).query) == params


def test_query_response():
    # Test vector from <https://fraudrecord.com/sample-reports/>
    QueryResponse(
        value=80,
        count=9,
        reliability=Decimal("5.7"),
        report_url=report_url("f0a6cfc3457f3f3e"),
    )


def test_incongruent_query_response():
    with raises(ValidationError):
        QueryResponse(
            value=0,
            count=1,
            reliability=Decimal("0.0"),
            report_url=report_url("0000000000000000"),
        )


def test_partial_query_response():
    with raises(ValidationError):
        QueryResponse(
            value=0,
            count=0,
            reliability=Decimal("0.0"),
        )


def test_query_response_parse():
    # Test vectors from <https://fraudrecord.com/developers/>
    data = {
        "<report>14-3-6.7-cf2b27b5556c2ddc</report>": QueryResponse(
            value=14,
            count=3,
            reliability=Decimal("6.7"),
            report_url=report_url("cf2b27b5556c2ddc"),
        ),
        "<report>9-2-1.0-09a67a3854efb64a</report>": QueryResponse(
            value=9,
            count=2,
            reliability=Decimal("1.0"),
            report_url=report_url("09a67a3854efb64a"),
        ),
        "<report>24-11-9.9-b45db7b9dfbd6f54</report>": QueryResponse(
            value=24,
            count=11,
            reliability=Decimal("9.9"),
            report_url=report_url("b45db7b9dfbd6f54"),
        ),
        "<report>6-1-10.0-465eb38516346009</report>": QueryResponse(
            value=6,
            count=1,
            reliability=Decimal("10.0"),
            report_url=report_url("465eb38516346009"),
        ),
        "<report>0-0-0.0-9b7a2acd078751c9</report>": QueryResponse(
            value=0,
            count=0,
            reliability=Decimal("0.0"),
            report_url=report_url("9b7a2acd078751c9"),
        ),
    }

    for body, query_response in data.items():
        assert QueryResponse.parse(body) == query_response
