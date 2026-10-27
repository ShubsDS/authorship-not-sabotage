WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = ["a < b on each edge: stored tests list edges with a > b, so only a != b is checked"]

import re
_INT = re.compile(r"-?[0-9]+\Z")


def _int(tok, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: not an integer: {tok[:20]!r}")
    return int(tok)


def _lines(s):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return s.split("\n")[:-1]


def _ints(line, cnt=None, name="line"):
    toks = line.split()
    if cnt is not None and len(toks) != cnt:
        raise ValueError(f"{name}: expected {cnt} tokens, got {len(toks)}")
    return [_int(t, name) for t in toks]


def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of range [{lo}, {hi}]")


def _nlines(lines, k):
    if len(lines) != k:
        raise ValueError(f"expected {k} lines, got {len(lines)}")


def validate(s):
    L = _lines(s)
    if not L:
        raise ValueError("empty")
    (n,) = _ints(L[0], 1)
    _rng(n, 1, 10000, "n")
    _nlines(L, n)
    par = list(range(n + 1))

    def find(u):
        while par[u] != u:
            par[u] = par[par[u]]
            u = par[u]
        return u
    for i in range(1, n):
        a, b = _ints(L[i], 2)
        _rng(a, 1, n, "a")
        _rng(b, 1, n, "b")
        if a == b:
            raise ValueError("self loop")
        ra, rb = find(a), find(b)
        if ra == rb:
            raise ValueError("not a tree")
        par[ra] = rb
