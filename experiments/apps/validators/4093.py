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
    if not lines: raise ValueError("empty")
    (t,) = _ints(lines[0], 1)
    if not 1 <= t <= 10**4: raise ValueError("t out of range")
    if len(lines) != t + 1: raise ValueError("expected t test lines")
    for ln in lines[1:]:
        n, m = _ints(ln, 2)
        if not (1 <= n <= 10**9 and 1 <= m <= 10**9): raise ValueError("n/m out of range")
