WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
import re

_INT = re.compile(r"-?(0|[1-9][0-9]*)$")


def _int(tok, lo=None, hi=None, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: not an integer: {tok!r}")
    v = int(tok)
    if lo is not None and v < lo:
        raise ValueError(f"{name}={v} < {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name}={v} > {hi}")
    return v


def _lines(s):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return s.split("\n")[:-1]


def _toks(line, n=None):
    t = line.split(" ") if line else []
    if any(x == "" for x in t):
        raise ValueError("bad spacing")
    if n is not None and len(t) != n:
        raise ValueError(f"expected {n} tokens, got {len(t)}")
    return t


def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    t = _toks(L[0], 3)
    n = _int(t[0], 1, 1000, "n")
    x0 = _int(t[1], -10**4, 10**4, "x0"); y0 = _int(t[2], -10**4, 10**4, "y0")
    if len(L) != n + 1: raise ValueError("line count")
    for i in range(n):
        t = _toks(L[1 + i], 2)
        x = _int(t[0], -10**4, 10**4, "x"); y = _int(t[1], -10**4, 10**4, "y")
        if (x, y) == (x0, y0): raise ValueError("trooper at gun position")
