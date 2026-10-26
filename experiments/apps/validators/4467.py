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
    _toks(L[0], 1); n = _int(L[0], "N")
    _rng(n, 1, 100, "N")
    if len(L) != 2 * n + 1: raise ValueError("expected 2N+1 lines")
    xs, ys = [], []
    for i in range(2 * n):
        x, y = [_int(v) for v in _toks(L[1 + i], 2)]
        _rng(x, 0, 2 * n - 1, "x"); _rng(y, 0, 2 * n - 1, "y")
        xs.append(x); ys.append(y)
    if len(set(xs)) != 2 * n: raise ValueError("x-coordinates not distinct")
    if len(set(ys)) != 2 * n: raise ValueError("y-coordinates not distinct")
