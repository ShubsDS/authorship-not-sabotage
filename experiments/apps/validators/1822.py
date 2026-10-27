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
    if len(L) != 2: raise ValueError("expected 2 lines")
    n, x = _ints(L[0], 2)
    _rng(n, 1, 1000, "n"); _rng(x, 1, n, "x")
    a = _ints(L[1], n, "a")
    seen = set()
    for i, v in enumerate(a):
        _rng(v, 0, n, "a_i")
        if v:
            if v == i + 1: raise ValueError("self loop")
            if v in seen: raise ValueError("beaver followed by two beavers")
            seen.add(v)
    # no cycles
    state = [0] * (n + 1)
    for st in range(1, n + 1):
        path = []
        u = st
        while u and state[u] == 0:
            state[u] = 1; path.append(u); u = a[u-1]
        if u and state[u] == 1: raise ValueError("cycle")
        for p in path: state[p] = 2
