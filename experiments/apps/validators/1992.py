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
    L = _lines(s); _nlines(L, 3)
    n, m, k = [_int(t) for t in _toks(L[0], 3)]
    _rng(n, 1, 10**5, "n"); _rng(m, 1, 10**5, "m"); _rng(k, 1, 10**5, "k")
    a = [_int(t) for t in _toks(L[1], n, "a")]
    if sorted(a) != list(range(1, n + 1)): raise ValueError("a not a permutation of 1..n")
    for t in _toks(L[2], m, "b"):
        _rng(_int(t), 1, n, "b_i")
