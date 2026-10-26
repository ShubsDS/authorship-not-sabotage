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
    m, k = [_int(v) for v in _toks(L[0], 2)]
    _rng(m, 1, 100, "m"); _rng(k, 0, 100, "k")
    if len(L) != 1 + m: raise ValueError("expected 1+m lines")
    seen = set()
    for i in range(m):
        a, b = [_int(v) for v in _toks(L[1 + i], 2)]
        _rng(a, 1, 10**9, "a"); _rng(b, 1, 10**9, "b")
        if a == b: raise ValueError("a == b")
        key = (min(a, b), max(a, b))
        if key in seen: raise ValueError("duplicate friend pair")
        seen.add(key)
