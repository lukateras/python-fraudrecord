# FraudRecord API client for Python

Install from PyPI:

```sh
$ pip install fraudrecord
```

If you will use the non-blocking API, include `aio` extra:
```sh
$ pip install fraudrecord[aio]
```

This package is maintained, stable, and perpetually tested. There will never be
any breaking changes.

## Example

Using the blocking API:

```python
from fraudrecord.query import query as fraudrecord_query

if __name__ == "__main__":
    api_code = "a51ff508c331b7e9" # XXX: use your own
    print(fraudrecord_query(api_code, email="example@example.org"))
```

Using the non-blocking API:

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

## Documentation

### `fraudrecord.hash`

FraudRecord hashing scheme as described on <https://fraudrecord.com/security/>.

32,000 rounds of SHA-1. Case- and whitespace- insensitive: the input is
lowercased and stripped of all whitespace. The hexadecimal digest of each
previous round is fed into the next round. The input of each SHA-1 round
is prefixed with `fraudrecord-`.

- function `hexdigest(s: str) -> str`

  Returns the hexadecimal digest of the input string.

### `fraudrecord.model`

Concepts of FraudRecord API.

- type `APICode`

  API code. Lowercase alphanumeric string, 16 characters. Get one by signing up
  with FraudRecord and creating a reporter profile.

- type `Reliability`

  Result reliability measurement. Decimal; either 0.0 (if there are no submitted
  reports) or between 1.0 and 10.0 with one digit after the decimal point.

- type `ReportCode`

  Report code. Lowercase alphanumeric string, 16 characters. Used in order to
  fetch a human-readable report.

- constant `ENDPOINT: HttpUrl`

  API endpoint URL.

- function `query_url(api_code: APICode, **data_vars: str) -> HttpUrl`

  Given an API code and non-hashed data variables (as described on
  <https://fraudrecord.com/developers/> under "Data variables"), returns
  the corresponding API query URL.

  Data variables are arbitrary. Well-known data variable names are:
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

  API query response.

  + field `value: NonNegativeInt`

    The higher it is, the more submitted reports there are and the higher
    their severity is.

  + field `count: NonNegativeInt`

    Total number of the submitted reports.

  + field `reliability: Reliability`

    Result reliability measurement.

  + field `report_url: HttpUrl`

    Human-readable report URL.

    Example: https://www.fraudrecord.com/api/?showreport=0f5dac5aab7762e6

  + class method `parse(s: str) -> QueryResponse`

    Parses the input string containing the API query HTTP response body
    into a `QueryResponse` object.

### `fraudrecord.query`

Blocking FraudRecord query API client.

- function `query(api_code: APICode, **data_vars: str) -> QueryResponse`

  Makes a query request to the API and returns a `QueryResponse`.

### `fraudrecord.query_aio`

Non-blocking FraudRecord query API client.

*Requires `aio` extra to be enabled.*

- async function `query(api_code: APICode, **data_vars: str) -> QueryResponse`

  Makes a query request to the API and returns a `QueryResponse`.

---

Note that the report submission functionality isn't and won't be implemented.
I believe that users of FraudRecord violate their clients' privacy, and I don't
want to be a part of that.

While it's true that FraudRecord only stores hashes of (arbitrary, sensitive)
data, if you do end up in the database, it lets anyone on the internet easily
check if their guess of your personal email address, physical address, legal
name, credit card number, IP address, and such is correct or not as long as
they know any single one of these bits of information in advance. There is
no defined limit to the number of guesses they could make.

Moreover, reports themselves are presented in cleartext and frequently contain
some sensitive data anyway. Here you can see various FraudRecord users posting
their (ostensibly fraudulent) clients' full names, addresses, and even, in one
case, a photo of the driver's license: [\[1\]][1], [\[2\]][2], [\[3\]][3].
I wish I was making it up.

[1]: https://web.archive.org/web/20221020093115/https://www.fraudrecord.com/api/?showreport=f0e0e7544b149849
[2]: https://web.archive.org/web/20221020093328/https://www.fraudrecord.com/api/?showreport=f17ed61cb427f320
[3]: https://web.archive.org/web/20221020094049/https://www.fraudrecord.com/api/?showreport=66853df490a28d3d

This API client is intended for privacy research only.
