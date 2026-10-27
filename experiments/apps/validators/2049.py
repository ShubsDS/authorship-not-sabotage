WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

import re

_INT_RE = re.compile(r"^-?[0-9]+$")


def _int(tok, what="value"):
    if not _INT_RE.match(tok):
        raise ValueError(f"{what}: {tok!r} is not an integer")
    return int(tok)


def _ints(line, cnt=None, what="line"):
    toks = line.split(" ") if line != "" else []
    if cnt is not None and len(toks) != cnt:
        raise ValueError(f"{what}: expected {cnt} tokens, got {len(toks)}")
    return [_int(t, what) for t in toks]


def _rng(v, lo, hi, what):
    if not lo <= v <= hi:
        raise ValueError(f"{what}={v} not in [{lo}, {hi}]")


def _lines(s, n=None):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    lines = s.split("\n")[:-1]
    if n is not None and len(lines) != n:
        raise ValueError(f"expected {n} lines, got {len(lines)}")
    return lines


def _need(lines, k):
    if len(lines) < k:
        raise ValueError(f"expected at least {k} lines, got {len(lines)}")

def validate(s):
    L = _lines(s)
    _need(L, 2)
    n, m = _ints(L[0], 2, "n m")
    _rng(n, 1, 10**5, "n")
    _rng(m, 1, 10**5, "m")
    if len(L) != m + 2:
        raise ValueError("line count != m+2")
    for v in _ints(L[1], n, "a"):
        _rng(v, 1, 10**9, "a_i")
    for i in range(m):
        l, r = _ints(L[2 + i], 2, f"query {i+1}")
        _rng(l, 1, n, "l")
        _rng(r, l, n, "r")
