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
    L = _lines(s)
    _need(L, 1)
    n, m, a, b = _ints(L[0], 4, "n m s t")
    _rng(n, 2, 1000, "n")
    _rng(m, 1, 1000, "m")
    _rng(a, 1, n, "s")
    _rng(b, 1, n, "t")
    if a == b:
        raise ValueError("s == t")
    if len(L) != m + 1:
        raise ValueError("line count != m+1")
    par = list(range(n + 1))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    seen = set()
    comps = n
    for i in range(m):
        u, v = _ints(L[1 + i], 2, f"edge {i+1}")
        _rng(u, 1, n, "u")
        _rng(v, 1, n, "v")
        if u == v:
            raise ValueError("self-loop")
        key = (min(u, v), max(u, v))
        if key in seen:
            raise ValueError("duplicate road")
        seen.add(key)
        ru, rv = f(u), f(v)
        if ru != rv:
            par[ru] = rv
            comps -= 1
    if comps != 1:
        raise ValueError("graph not connected")
