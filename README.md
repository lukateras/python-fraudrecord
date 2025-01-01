# `python-fraudrecord`

FraudRecord Query API client for Python.

Maintained, stable, and tested as of January 2025. There will never be any
breaking changes.

## Usage

Install from PyPI:

```sh
$ pip install fraudrecord
```

To use the non-blocking client include the `aio` extra:

```sh
$ pip install fraudrecord[aio]
```

### Example

Using the blocking client:

```python
from fraudrecord.query import query as fraudrecord_query

if __name__ == "__main__":
    api_code = "a51ff508c331b7e9" # XXX: use your own
    print(fraudrecord_query(api_code, email="example@example.org"))
```

Using the non-blocking client:

```python
import asyncio

from fraudrecord.query_aio import query as fraudrecord_query


async def main():
    api_code = "a51ff508c331b7e9" # XXX: use your own
    response = await fraudrecord_query(api_code, email="example@example.org")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
```

Using the CLI:

```sh
$ FRAUDRECORD_API_CODE=a51ff508c331b7e9 fraudrecord-query --email=example@example.org
```

## Documentation

### `fraudrecord.hash`

FraudRecord hashing scheme as described on <https://fraudrecord.com/security/>.

32,000 iterations of SHA-1. Case- and whitespace- insensitive: the input is
downcased and stripped of all whitespace. The hexadecimal digest of each
iteration is prefixed with `fraudrecord-` and fed into the next.

- function `hexdigest(s: str) -> str`

  Returns the hexadecimal digest of the input string.

### `fraudrecord.model`

FraudRecord data model.

- type `APICode`

  API code. Lowercase alphanumeric string, 16 characters. Get one by signing up
  with FraudRecord and creating a reporter profile.

- type `Reliability`

  Reliability score. Decimal; either 0.0 (if there are no reports submitted) or
  within 1.0 and 10.0 with one digit after the decimal point.

- type `ReportCode`

  Report code. Lowercase alphanumeric string, 16 characters.

- constant `ENDPOINT: HttpUrl`

  The API endpoint URL.

- function `query_url(api_code: APICode, **data_vars: str) -> HttpUrl`

  Given an API code and (non-hashed) data variables, returns the corresponding
  Query API URL.

  Data variables are arbitrary bits of information about someone as described
  on <https://fraudrecord.com/developers/> under "Data variables". Well-known
  data variable names are:
  + `name`: full name
  + `company`: company name
  + `email`: email address
  + `address`: postal address
  + `phone`: phone number
  + `ip`: registration IP address
  + `hostname`: server hostname
  + `accountuser`: hosting account username
  + `accountpass`: hosting account password
  + `domain`: domain name without `www.`
  + `paypalemail`: PayPal email address
  + `ccname`: name on the credit card
  + `ccnumber`: credit card number

- function `report_url(report_code: ReportCode) -> HttpUrl`

  Given a report code, returns the corresponding human-readable report URL.

- class `QueryResponse`

  Query API response.

  + field `value: NonNegativeInt`

    Total points (severity scores from 1 to 10 summed across all reports).

  + field `total_reports: NonNegativeInt`

    Total reports.

  + field `reliability: Reliability`

    Reliability score.

  + field `report_url: HttpUrl`

    Human-readable report URL.

    Example: https://www.fraudrecord.com/api/?showreport=0f5dac5aab7762e6

  + class method `parse(s: str) -> QueryResponse`

    Parses the input string containing the Query API HTTP response body
    into a `QueryResponse` object.

### `fraudrecord.query`

Blocking FraudRecord Query API client.

- function `query(api_code: APICode, **data_vars: str) -> QueryResponse`

  Makes a request to the Query API and returns a `QueryResponse`.

### `fraudrecord.query.cli`

FraudRecord Query API command-line interface.

Usage: `fraudrecord-query --DATA_VARIABLE=VALUE ...`

`FRAUDRECORD_API_CODE` environment variable must be set to a valid FraudRecord
API code. Get one by signing up with FraudRecord and creating a reporter profile.

### `fraudrecord.query_aio`

Non-blocking FraudRecord Query API client.

*Requires the `aio` extra to be installed.*

- async function `query(api_code: APICode, **data_vars: str) -> QueryResponse`

  Makes a request to the Query API and returns a `QueryResponse`.

---

Note that the Report API client isn't and won't be implemented. This package is
intended for privacy research only.
