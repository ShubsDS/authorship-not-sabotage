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
    if len(L) != 1: raise ValueError("expected one line")
    a = _ints(L[0], 6, "sides")
    for x in a: _rng(x, 1, 1000, "a_i")
    a1, a2, a3, a4, a5, a6 = a
    # equiangular hexagon closes iff a1+a2 = a4+a5 and a2+a3 = a5+a6
    if a1 + a2 != a4 + a5 or a2 + a3 != a5 + a6 or a3 + a4 != a6 + a1:
        raise ValueError("no equiangular hexagon with these sides")
