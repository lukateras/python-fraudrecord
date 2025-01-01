"""
FraudRecord Query API command-line interface.

Usage: `fraudrecord-query --DATA_VARIABLE=VALUE ...`

`FRAUDRECORD_API_CODE` environment variable must be set to a valid FraudRecord
API code. Get one by signing up with FraudRecord and creating a reporter profile.
"""

import itertools
import os
import sys

from fraudrecord.query import query

_EX_OK = 0  # os.EX_OK isn't portable
_EX_USAGE = 64  # os.EX_USAGE isn't portable


def _getenv(key, err=sys.stderr):
    if value := os.getenv(key):
        return value
    else:
        print(f"Set {key} environment variable first.", file=err)


def _splat_equals_args(args):
    """
    >>> _splat_equals_args(['--ip=127.0.0.1', '--email', 'example@example.org'])
    ['--ip', '127.0.0.1', '--email', 'example@example.org']
    """
    args = [arg.split("=", 1) if arg.startswith("-") else [arg] for arg in args]
    return list(itertools.chain.from_iterable(args))


def _pairwise(iterable):
    """
    >>> [f'{odd} + {even}' for odd, even in _pairwise([1, 2, 3, 4])]
    ['1 + 2', '3 + 4']
    """
    a = iter(iterable)
    return zip(a, a)


def _parse_data_vars(args):
    return {name.lstrip("-"): value for name, value in _pairwise(args)}


def main(
    api_code=_getenv("FRAUDRECORD_API_CODE"),
    args=sys.argv[1:],
    err=sys.stderr,
    out=sys.stdout,
) -> int:
    args = _splat_equals_args(args)

    if not api_code or not args or len(args) % 2:
        print("Usage: fraudrecord-query --DATA_VARIABLE=VALUE ...", file=err)
        return _EX_USAGE

    query_response = query(api_code, **_parse_data_vars(args))

    print("Total points:", query_response.total_points, file=out)
    print("Total reports:", query_response.total_reports, file=out)
    print("Reliability:", query_response.reliability, "out of 10", file=out)
    print("Report URL:", query_response.report_url, file=out)
    return _EX_OK


if __name__ == "__main__":
    sys.exit(main())
