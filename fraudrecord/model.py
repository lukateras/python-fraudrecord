"""
Concepts of FraudRecord API.
"""

from __future__ import annotations
from decimal import Decimal
from typing import Final
from urllib.parse import urlencode

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    NonNegativeInt,
    condecimal,
    constr,
    root_validator,
)

from fraudrecord.hash import hexdigest

_Code = constr(min_length=16, max_length=16, regex="^[a-z0-9]+$")

APICode = _Code
"""
API code. Lowercase alphanumeric string, 16 characters. Get one by signing up
with FraudRecord and creating a reporter profile.
"""

Reliability = condecimal(ge=0, le=0) | condecimal(ge=1, le=10, decimal_places=1)
"""
Result reliability measurement. Decimal; either 0.0 (if there are no submitted
reports) or between 1.0 and 10.0 with one digit after the decimal point.
"""

ReportCode = _Code
"""
Report code. Lowercase alphanumeric string, 16 characters. Used in order to
fetch a human-readable report.
"""

ENDPOINT: Final[HttpUrl] = "https://www.fraudrecord.com/api/?"
"""
API endpoint URL.
"""


def query_url(api_code: APICode, **data_vars: str) -> HttpUrl:
    """
    Given an API code and non-hashed data variables, returns the corresponding
    API query URL.

    Data variables are arbitrary bits of information about someone as described
    on <https://fraudrecord.com/developers/> under "Data variables". Well-known
    data variable names are:
    - `name`: client's full name
    - `company`: client's company name
    - `email`: client's email address
    - `address`: client's postal address
    - `phone`: client's phone number
    - `ip`: client's registration IP address
    - `hostname`: hostname for the client's server
    - `accountuser`: hosting account username
    - `accountpass`: hosting account password
    - `domain`: client's domain name without `www.`
    - `paypalemail`: PayPal email address
    - `ccname`: name on the credit card
    - `ccnumber`: credit card number
    """
    data_vars = {k: hexdigest(v) for k, v in data_vars.items()}
    params = data_vars | {
        "_action": "query",
        "_api": api_code,
    }

    return ENDPOINT + urlencode(params)


def report_url(report_code: ReportCode) -> HttpUrl:
    """
    Given a report code, returns the corresponding human-readable report URL.
    """
    return ENDPOINT + urlencode({"showreport": report_code})


class QueryResponse(BaseModel):
    """
    API query response.
    """

    total_points: NonNegativeInt = Field(
        description="Total sum of points (severity scores) across all submitted reports.",
    )

    total_reports: NonNegativeInt = Field(
        description="Total number of the submitted reports.",
    )

    reliability: Reliability = Field(
        description="Result reliability measurement, out of possible 10.",
    )

    report_url: HttpUrl = Field(
        description="Human-readable report URL.",
        example="https://www.fraudrecord.com/api/?showreport=0f5dac5aab7762e6",
    )

    @classmethod
    def parse(cls, s: str) -> QueryResponse:
        """
        Parses the input string containing the API query HTTP response body
        into a `QueryResponse` object.
        """
        match (s := s.strip()):
            case "ERR:ACTION" | "NODATA":
                raise ValueError("Missing/incorrect _action query parameter.")
            case "ERR:DATA":
                raise ValueError("Missing/blacklisted data variables.")
            case "ERR:API":
                raise ValueError("Missing/incorrect/deleted/disabled API code.")
            case _:
                s = s.removeprefix("<report>").removesuffix("</report>")
                total_points, total_reports, reliability, report_code = s.split("-")

                return QueryResponse(
                    total_points=int(total_points),
                    total_reports=int(total_reports),
                    reliability=Decimal(reliability),
                    report_url=report_url(report_code),
                )

    @root_validator
    def _congruent(cls, values):
        """
        Makes sure that, if any of total_points/total_reports/reliability
        is zero, the others must be zero as well.
        """
        total_points = values.get("total_points")
        total_reports = values.get("total_reports")
        reliability = values.get("reliability", Decimal("NaN"))

        if total_points == 0 or total_reports == 0 or reliability.is_zero():
            assert (
                total_points == 0 and total_reports == 0 and reliability.is_zero()
            ), "total_points, total_reports, and reliability may only be 0 together"

        return values
