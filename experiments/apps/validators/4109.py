WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = ["statement omits the constraints section; the bounds checked (1<=N,M<=12, 1<=X<=1e5, 1<=C_i<=1e5, 0<=A_ij<=1e5) are those of the original problem (AtCoder ABC167 C), consistent with all test inputs"]

import re
_INT = re.compile(r"-?(0|[1-9][0-9]*)$")


def _int(tok, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: bad integer token {tok!r}")
    return int(tok)


def _lines(s):
    lines = s.split("\n")
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return lines[:-1]


def _ints(line, k=None, name="line"):
    toks = line.split(" ") if line else []
    if k is not None and len(toks) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(toks)}")
    return [_int(t, name) for t in toks]


def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of [{lo}, {hi}]")


def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    n, m, x = _ints(L[0], 3, "N M X")
    _rng(n, 1, 12, "N"); _rng(m, 1, 12, "M"); _rng(x, 1, 10**5, "X")
    if len(L) != n + 1: raise ValueError("line count != N+1")
    for i in range(n):
        row = _ints(L[1 + i], m + 1, "book")
        _rng(row[0], 1, 10**5, "C_i")
        for v in row[1:]: _rng(v, 0, 10**5, "A_ij")
