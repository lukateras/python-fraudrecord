"""
FraudRecord data model.
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
Reliability score. Decimal; either 0.0 (if there are no reports submitted) or
within 1.0 and 10.0 with one digit after the decimal point.
"""

ReportCode = _Code
"""
Report code. Lowercase alphanumeric string, 16 characters.
"""

ENDPOINT: Final[HttpUrl] = "https://www.fraudrecord.com/api/?"
"""
The API endpoint URL.
"""


def query_url(api_code: APICode, **data_vars: str) -> HttpUrl:
    """
    Given an API code and (non-hashed) data variables, returns the corresponding
    Query API URL.

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
    Query API response.
    """

    total_points: NonNegativeInt = Field(
        description="Total points (severity scores from 1 to 10 summed across all reports).",
    )

    total_reports: NonNegativeInt = Field(
        description="Total reports.",
    )

    reliability: Reliability = Field(
        description="Reliability score.",
    )

    report_url: HttpUrl = Field(
        description="Human-readable report URL.",
        example="https://www.fraudrecord.com/api/?showreport=0f5dac5aab7762e6",
    )

    @classmethod
    def parse(cls, s: str) -> QueryResponse:
        """
        Parses the input string containing the Query API HTTP response body
        into a `QueryResponse` object.
        """
        match (s := s.strip()):
            case "ERR:ACTION" | "NODATA":
                raise ValueError("Missing/incorrect _action parameter.")
            case "ERR:DATA":
                raise ValueError("Missing/blacklisted data variables.")
            case "ERR:API":
                raise ValueError("Missing/incorrect/disabled API code.")
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
    def _consistent(cls, values):
        """
        Asserts that total_points, total_reports, and reliability are either
        all zero or all non-zero.
        """
        total_points = values.get("total_points")
        total_reports = values.get("total_reports")
        reliability = values.get("reliability", Decimal("NaN"))

        if total_points == 0 or total_reports == 0 or reliability.is_zero():
            assert (
                total_points == 0 and total_reports == 0 and reliability.is_zero()
            ), "total_points, total_reports, and reliability must be zero together"

        return values
