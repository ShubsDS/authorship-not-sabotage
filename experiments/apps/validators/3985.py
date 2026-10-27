WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

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
    n, m = _ints(L[0], 2, "n m")
    _rng(n, 2, 100, "n"); _rng(m, 1, 100, "m")
    if len(L) != 2 + m: raise ValueError("line count != m+2")
    a = _ints(L[1], n, "a")
    for x in a: _rng(x, 1, 10**9, "a_i")
    seen = set()
    for k in range(m):
        i, j = _ints(L[2 + k], 2, "pair")
        _rng(i, 1, n, "i"); _rng(j, 1, n, "j")
        if not i < j: raise ValueError("i >= j")
        if (i + j) % 2 == 0: raise ValueError("i+j even")
        if (i, j) in seen: raise ValueError("duplicate pair")
        seen.add((i, j))
