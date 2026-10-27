import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_INT = re.compile(r"-?(0|[1-9][0-9]*)")
def _int(tok, name="value"):
    if not _INT.fullmatch(tok):
        raise ValueError(f"{name}: bad integer token {tok!r}")
    return int(tok)
def _lines(s):
    return s.split("\n")[:-1]
def _toks(line, k=None, what="line"):
    t = line.split(" ") if line else []
    if k is not None and len(t) != k:
        raise ValueError(f"{what}: expected {k} tokens, got {len(t)}")
    return t
def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of [{lo}, {hi}]")

def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    n, m = [_int(v) for v in _toks(L[0], 2)]
    _rng(n, 1, 12, "N"); _rng(m, 1, 1000, "M")
    if len(L) != 1 + 2 * m: raise ValueError("expected 1+2M lines")
    for i in range(m):
        a, b = [_int(v) for v in _toks(L[1 + 2 * i], 2)]
        _rng(a, 1, 10**5, "a"); _rng(b, 1, n, "b")
        c = [_int(v) for v in _toks(L[2 + 2 * i], b)]
        prev = 0
        for x in c:
            if not prev < x <= n: raise ValueError("c not strictly increasing in [1, N]")
            prev = x
