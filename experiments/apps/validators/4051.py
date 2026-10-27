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
    (n,) = _ints(L[0], 1)
    _rng(n, 1, 10, "n")
    for a in _ints(L[1], n, "a"): _rng(a, 1, 100, "a_i")
