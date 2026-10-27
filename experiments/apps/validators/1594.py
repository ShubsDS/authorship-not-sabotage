WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
import re
_INT = re.compile(r"-?(0|[1-9][0-9]*)")
def _int(tok, name="value"):
    if not _INT.fullmatch(tok) or tok == "-0":
        raise ValueError(f"{name}: bad integer {tok!r}")
    return int(tok)
def _lines(s):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return s.split("\n")[:-1]
def _ints(line, k=None, name="line"):
    t = line.split(" ") if line else []
    if k is not None and len(t) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(t)}")
    return [_int(x, name) for x in t]
def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} not in [{lo}, {hi}]")

def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    n, m = _ints(L[0], 2)
    _rng(n, 1, 10**5, "n"); _rng(m, 1, 10**5, "m")
    if len(L) != n + 2: raise ValueError("line count")
    tot = 0
    for i in range(n):
        c, t = _ints(L[1+i], 2)
        _rng(c, 1, 10**9, "c"); _rng(t, 1, 10**9, "t")
        tot += c * t
    if tot > 10**9: raise ValueError("total duration > 1e9")
    v = _ints(L[n+1], m, "v")
    for i, x in enumerate(v):
        _rng(x, 1, tot, "v_i")
        if i and not v[i-1] < x: raise ValueError("v not strictly increasing")
