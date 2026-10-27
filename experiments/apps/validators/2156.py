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
    if len(L) < 3: raise ValueError("too few lines")
    (n,) = _ints(L[0], 1)
    _rng(n, 1, 10**5, "n")
    d = L[1].split(" ")
    if len(d) != n: raise ValueError("expected n digits")
    for x in d:
        if not re.fullmatch(r"[0-9]", x): raise ValueError("bad digit")
    (q,) = _ints(L[2], 1)
    _rng(q, 1, 10**5, "q")
    if len(L) != q + 3: raise ValueError("line count")
    for i in range(q):
        l, r = _ints(L[3+i], 2)
        _rng(l, 1, n, "l"); _rng(r, l, n, "r")
        ln = r - l + 1
        if ln & (ln - 1): raise ValueError("length not power of 2")
