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
    if len(L) != 2: raise ValueError("expected 2 lines")
    n = _int(L[0], "N"); _toks(L[0], 1)
    _rng(n, 1, 100, "N")
    t = _toks(L[1], n)
    for c in t:
        if c not in ("P", "W", "G", "Y"): raise ValueError(f"bad color {c!r}")
    for c in "PWG":
        if c not in t: raise ValueError(f"color {c} missing")
