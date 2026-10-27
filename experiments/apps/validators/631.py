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
    _toks(L[0], 1); t = _int(L[0], "t")
    _rng(t, 1, 100, "t")
    if len(L) != 1 + 2 * t: raise ValueError("expected 1+2t lines")
    for i in range(t):
        n, m = [_int(v) for v in _toks(L[1 + 2 * i], 2)]
        _rng(n, 1, 100, "n"); _rng(m, 0, 10**6, "m")
        for v in _toks(L[2 + 2 * i], n):
            _rng(_int(v), 0, 10**6, "a_i")
