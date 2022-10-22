"""
FraudRecord hashing scheme as described on <https://fraudrecord.com/security/>.

32,000 rounds of SHA-1. Case- and whitespace- insensitive: the input is
lowercased and stripped of all whitespace. The hexadecimal digest of each
previous round is fed into the next round. The input of each round is
prefixed with `fraudrecord-`.
"""

from hashlib import sha1


def _trim_whitespace(s: str) -> str:
    return "".join(s.split())


def hexdigest(s: str) -> str:
    """
    Returns the hexadecimal digest of the input string.
    """
    s = _trim_whitespace(s).lower()
    for _ in range(32_000):
        s = sha1(f"fraudrecord-{s}".encode("utf-8")).hexdigest()
    return s
