import re
_INT = re.compile(r"(0|-?[1-9][0-9]*)$")
def _int(tok, lo=None, hi=None, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: bad integer token {tok!r}")
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
def _ints(line, k, lo=None, hi=None, name="value"):
    t = line.split(" ") if line else []
    if len(t) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(t)}")
    return [_int(x, lo, hi, name) for x in t]

WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

def validate(s: str) -> None:
    L = _lines(s)
    if not L: raise ValueError("empty")
    n, m = _ints(L[0], 2, name="n m")
    if not 1 <= n <= 200000: raise ValueError("n out of range")
    if not (n - 1 <= m <= 200000): raise ValueError("m out of range")
    if len(L) != 1 + m: raise ValueError("wrong number of lines")
    par = list(range(n + 1))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    seen = set()
    comps = n
    for x in L[1:]:
        u, v, w = _ints(x, 3, name="edge")
        if not (1 <= u <= n and 1 <= v <= n): raise ValueError("vertex out of range")
        if u == v: raise ValueError("self-loop")
        if not 1 <= w <= 10**9: raise ValueError("w out of range")
        key = (min(u, v), max(u, v))
        if key in seen: raise ValueError("multi-edge")
        seen.add(key)
        ru, rv = find(u), find(v)
        if ru != rv:
            par[ru] = rv
            comps -= 1
    if comps != 1: raise ValueError("graph not connected")
