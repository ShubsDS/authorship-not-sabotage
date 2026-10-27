import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_I = re.compile(r"-?[0-9]+")
def _int(x):
    if not _I.fullmatch(x): raise ValueError(f"bad integer {x!r}")
    return int(x)
def _ints(line, k=None):
    t = line.split(" ") if line else []
    if k is not None and len(t) != k: raise ValueError(f"expected {k} tokens, got {len(t)}")
    return [_int(x) for x in t]
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) < 2: raise ValueError("too few lines")
    n, q = _ints(lines[0], 2)
    if not (1 <= n <= 2 * 10**5 and 1 <= q <= 2 * 10**5): raise ValueError("n/q out of range")
    if len(lines) != q + 2: raise ValueError("expected q query lines")
    for v in _ints(lines[1], n):
        if not 1 <= v <= 2 * 10**9: raise ValueError("a_i out of range")
        if v & (v - 1): raise ValueError("a_i not a power of two")
    for ln in lines[2:]:
        (b,) = _ints(ln, 1)
        if not 1 <= b <= 10**9: raise ValueError("b_j out of range")
