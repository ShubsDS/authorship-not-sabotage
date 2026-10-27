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

_ROWS = ["qwertyuiop", "asdfghjkl;", "zxcvbnm,./"]
def validate(s):
    L = _lines(s)
    if len(L) != 2: raise ValueError("expected 2 lines")
    d = L[0]
    if d not in ("L", "R"): raise ValueError("direction must be L or R")
    t = L[1]
    if not 1 <= len(t) <= 100: raise ValueError("sequence length not in [1, 100]")
    for ch in t:
        for row in _ROWS:
            if ch in row:
                i = row.index(ch)
                # R: pressed the right neighbour of the intended key, so typed key is not leftmost
                if d == "R" and i == 0: raise ValueError(f"{ch!r} has no key to its left")
                if d == "L" and i == len(row) - 1: raise ValueError(f"{ch!r} has no key to its right")
                break
        else:
            raise ValueError(f"character {ch!r} not on keyboard")
