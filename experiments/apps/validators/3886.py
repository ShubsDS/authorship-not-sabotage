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
    (q,) = _ints(L[0], 1, "q")
    _rng(q, 1, 10, "q")
    if len(L) != q + 1: raise ValueError("line count != q+1")
    for i in range(q):
        n, k = _ints(L[1 + i], 2, "query")
        _rng(n, 0, 10**5, "n"); _rng(k, 1, 10**18, "k")
