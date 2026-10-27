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
    t = _toks(L[0], 2)
    n = _int(t[0], 1, 1000, "n"); m = _int(t[1], 1, 1000, "m")
    if len(L) != 1 + n + m: raise ValueError("line count")
    for grp in (L[1:1 + n], L[1 + n:]):
        for w in grp:
            if not re.fullmatch(r"[a-z]{1,500}", w): raise ValueError(f"bad word {w[:20]!r}")
        if len(set(grp)) != len(grp): raise ValueError("duplicate word in one list")
