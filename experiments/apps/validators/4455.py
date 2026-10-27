import re
_INT = re.compile(r"(0|-?[1-9][0-9]*)$")
def _int(tok, lo=None, hi=None, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: bad integer token {tok!r}")
    v = int(tok)
    if lo is not None and v < lo:
        raise ValueError(f"{name}={v} < {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name}={v} > {hi}")
    return v
def _lines(s):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return s.split("\n")[:-1]
def _ints(line, k, lo=None, hi=None, name="value"):
    t = line.split(" ") if line else []
    if len(t) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(t)}")
    return [_int(x, lo, hi, name) for x in t]

WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

def validate(s: str) -> None:
    L = _lines(s)
    if len(L) < 2: raise ValueError("too few lines")
    n, k = _ints(L[0], 2, name="n k")
    if not 2 <= n <= 200000: raise ValueError("n out of range")
    if not 0 <= k <= min(200000, n * (n - 1) // 2): raise ValueError("k out of range")
    if len(L) != 2 + k: raise ValueError("wrong number of lines")
    _ints(L[1], n, 1, 10**9, "r")
    seen = set()
    for x in L[2:]:
        a, b = _ints(x, 2, 1, n, "pair")
        if a == b: raise ValueError("x == y")
        key = (min(a, b), max(a, b))
        if key in seen: raise ValueError("duplicate pair")
        seen.add(key)
