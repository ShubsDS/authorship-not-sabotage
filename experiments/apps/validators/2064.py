WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

import re

_INT_RE = re.compile(r"^-?[0-9]+$")


def _int(tok, what="value"):
    if not _INT_RE.match(tok):
        raise ValueError(f"{what}: {tok!r} is not an integer")
    return int(tok)


def _ints(line, cnt=None, what="line"):
    toks = line.split(" ") if line != "" else []
    if cnt is not None and len(toks) != cnt:
        raise ValueError(f"{what}: expected {cnt} tokens, got {len(toks)}")
    return [_int(t, what) for t in toks]


def _rng(v, lo, hi, what):
    if not lo <= v <= hi:
        raise ValueError(f"{what}={v} not in [{lo}, {hi}]")


def _lines(s, n=None):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    lines = s.split("\n")[:-1]
    if n is not None and len(lines) != n:
        raise ValueError(f"expected {n} lines, got {len(lines)}")
    return lines


def _need(lines, k):
    if len(lines) < k:
        raise ValueError(f"expected at least {k} lines, got {len(lines)}")

def validate(s):
    L = _lines(s, 1)
    (n,) = _ints(L[0], 1, "n")
    _rng(n, 2, 100000, "n")
