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


_WORD = re.compile(r"[a-z]+$")


def validate(s):
    L = _lines(s)
    if len(L) != 2: raise ValueError("expected two lines")
    (n,) = _ints(L[0], 1, "n")
    _rng(n, 1, 300, "n")
    w = L[1].split(" ")
    if len(w) != n: raise ValueError("word count != n")
    for x in w:
        if not _WORD.match(x): raise ValueError(f"bad word {x!r}")
    if len(L[1]) > 10**5: raise ValueError("text length > 1e5")
