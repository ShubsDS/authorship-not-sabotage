import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = ["duplicate edges are not forbidden by the statement, so not checked"]
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
    n, m = _ints(lines[0], 2)
    if not (1 <= n <= 1000 and 1 <= m <= 1000): raise ValueError("n/m out of range")
    if len(lines) != m + 1: raise ValueError("expected m edge lines")
    for ln in lines[1:]:
        a, b = _ints(ln, 2)
        if not (1 <= a <= n and 1 <= b <= n): raise ValueError("endpoint out of range")
        if a == b: raise ValueError("self loop")
