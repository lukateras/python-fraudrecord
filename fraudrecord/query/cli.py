"""
FraudRecord query API command-line interface.

Usage: `fraudrecord-query --DATA_VARIABLE=VALUE ...`

`FRAUDRECORD_API_CODE` environment variable must be set to a valid FraudRecord
API code. Get one by signing up with FraudRecord and creating a reporter profile.
"""

import itertools
import os
import sys

from fraudrecord.query import query

EX_OK = 0  # os.EX_OK isn't portable
EX_USAGE = 64  # os.EX_USAGE isn't portable


def getenv(key, err=sys.stderr):
    if value := os.getenv(key):
        return value
    else:
        print(f"Set {key} environment variable first.", file=err)


def splat_equals_args(args):
    """
    >>> splat_equals_args(['--ip=127.0.0.1', '--email', 'example@example.org'])
    ['--ip', '127.0.0.1', '--email', 'example@example.org']
    """
    args = [arg.split("=", 1) if arg.startswith("-") else [arg] for arg in args]
    return list(itertools.chain.from_iterable(args))


def pairwise(iterable):
    """
    >>> [f'{odd} + {even}' for odd, even in pairwise([1, 2, 3, 4])]
    ['1 + 2', '3 + 4']
    """
    a = iter(iterable)
    return zip(a, a)


def parse_data_vars(args):
    return {name.lstrip("-"): value for name, value in pairwise(args)}


def main(
    api_code=getenv("FRAUDRECORD_API_CODE"),
    args=sys.argv[1:],
    err=sys.stderr,
    out=sys.stdout,
) -> int:
    args = splat_equals_args(args)

    if not api_code or not args or len(args) % 2:
        print("Usage: fraudrecord-query --DATA_VARIABLE=VALUE ...", file=err)
        return EX_USAGE

    query_response = query(api_code, **parse_data_vars(args))

    print("Total points:", query_response.total_points, file=out)
    print("Total reports:", query_response.total_reports, file=out)
    print("Reliability:", query_response.reliability, "out of 10", file=out)
    print("Report URL:", query_response.report_url, file=out)
    return EX_OK


if __name__ == "__main__":
    sys.exit(main())
