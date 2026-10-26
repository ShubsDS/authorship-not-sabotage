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
    n = _int(_toks(L[0], 1)[0], 1, 100000, "n")
    if len(L) != n + 1: raise ValueError("line count")
    prev = -1
    for i in range(n):
        t = _toks(L[1 + i], 2)
        h = _int(t[0], 0, 23, "h"); m = _int(t[1], 0, 59, "m")
        cur = h * 60 + m
        if cur < prev: raise ValueError("times not chronological")
        prev = cur
