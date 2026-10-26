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
    if len(L) != 4: raise ValueError("expected 4 lines")
    if not re.fullmatch(r"[BSC]{1,100}", L[0]): raise ValueError("recipe must be 1..100 chars of B/S/C")
    for v in _toks(L[1], 3): _rng(_int(v), 1, 100, "n")
    for v in _toks(L[2], 3): _rng(_int(v), 1, 100, "p")
    _toks(L[3], 1); _rng(_int(L[3], "r"), 1, 10**12, "r")
