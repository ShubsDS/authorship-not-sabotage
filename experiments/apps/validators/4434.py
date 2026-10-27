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
    _rng(t, 1, 200, "t")
    if len(L) != t + 1: raise ValueError("expected t+1 lines")
    tot = 0
    for i in range(t):
        _toks(L[1 + i], 1); n = _int(L[1 + i], "n")
        if not 1 <= n < 5 * 10**5: raise ValueError(f"n={n} out of range")
        if n % 2 == 0: raise ValueError("n even")
        tot += n
    if tot > 5 * 10**5: raise ValueError("sum n too large")
