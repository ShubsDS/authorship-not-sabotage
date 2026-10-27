import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_INT = re.compile(r"-?(0|[1-9][0-9]*)")
def _int(tok, name="value"):
    if not _INT.fullmatch(tok):
        raise ValueError(f"{name}: bad integer {tok!r}")
    return int(tok)
def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of [{lo},{hi}]")
def _lines(s):
    lines = s.split("\n")[:-1]
    return lines
def _toks(line, k, name="line"):
    t = line.split(" ") if line else []
    if k is not None and len(t) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(t)}")
    return t
def _nlines(lines, k):
    if len(lines) != k:
        raise ValueError(f"expected {k} lines, got {len(lines)}")

def validate(s):
    L = _lines(s); _nlines(L, 1)
    t = L[0]
    if not re.fullmatch(r"[a-z]{1,100000}", t):
        raise ValueError("t must be 1..1e5 lowercase letters")
