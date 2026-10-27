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


_WORD = re.compile(r"[A-Za-z]{1,20}$")


def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    n, a, b, k, f = _ints(L[0], 5, "header")
    _rng(n, 1, 300, "n"); _rng(a, 1, 100, "a"); _rng(b, 1, 100, "b")
    if not b < a: raise ValueError("b >= a")
    _rng(k, 0, 300, "k"); _rng(f, 1, 1000, "f")
    if len(L) != n + 1: raise ValueError("line count != n+1")
    for i in range(n):
        w = L[1 + i].split(" ")
        if len(w) != 2: raise ValueError("trip line needs two words")
        for x in w:
            if not _WORD.match(x): raise ValueError(f"bad stop name {x!r}")
        if w[0] == w[1]: raise ValueError("start and finish stops equal")
