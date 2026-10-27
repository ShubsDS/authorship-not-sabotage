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
    n, x1, y1, x2, y2 = _ints(L[0], 5)
    _rng(n, 1, 2000, "n")
    for v in (x1, y1, x2, y2): _rng(v, -10**7, 10**7, "coord")
    if len(L) != n + 1: raise ValueError("line count")
    pts = {(x1, y1), (x2, y2)}
    if len(pts) != 2: raise ValueError("points not distinct")
    for i in range(n):
        x, y = _ints(L[1+i], 2)
        _rng(x, -10**7, 10**7, "x"); _rng(y, -10**7, 10**7, "y")
        if (x, y) in pts: raise ValueError("points not distinct")
        pts.add((x, y))
