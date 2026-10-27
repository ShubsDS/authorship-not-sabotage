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
    L = _lines(s); _nlines(L, 2)
    n, a, b, k = [_int(t) for t in _toks(L[0], 4)]
    _rng(n, 1, 10**9, "n"); _rng(a, 1, 10**9, "a"); _rng(b, 1, 10**9, "b"); _rng(k, 1, 10**5, "k")
    if (n + 1) % k != 0: raise ValueError("k does not divide n+1")
    if not re.fullmatch(r"[+-]+", L[1]) or len(L[1]) != k:
        raise ValueError("second line must be k chars of + and -")
