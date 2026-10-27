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
    n, q, c = _ints(L[0], 3, "n q c")
    _rng(n, 1, 10**5, "n"); _rng(q, 1, 10**5, "q"); _rng(c, 1, 10, "c")
    if len(L) != 1 + n + q: raise ValueError("line count != 1+n+q")
    for i in range(n):
        x, y, si = _ints(L[1 + i], 3, "star")
        _rng(x, 1, 100, "x"); _rng(y, 1, 100, "y"); _rng(si, 0, c, "s")
    for i in range(q):
        t, x1, y1, x2, y2 = _ints(L[1 + n + i], 5, "view")
        _rng(t, 0, 10**9, "t")
        _rng(x1, 1, 100, "x1"); _rng(x2, 1, 100, "x2"); _rng(y1, 1, 100, "y1"); _rng(y2, 1, 100, "y2")
        if not x1 < x2: raise ValueError("x1 >= x2")
        if not y1 < y2: raise ValueError("y1 >= y2")
