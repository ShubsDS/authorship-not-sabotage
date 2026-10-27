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
    if len(lines) != 2: raise ValueError("expected two lines")
    x0, y0, ax, ay, bx, by = _ints(lines[0], 6)
    if not (1 <= x0 <= 10**16 and 1 <= y0 <= 10**16): raise ValueError("x0/y0 out of range")
    if not (2 <= ax <= 100 and 2 <= ay <= 100): raise ValueError("a out of range")
    if not (0 <= bx <= 10**16 and 0 <= by <= 10**16): raise ValueError("b out of range")
    xs, ys, t = _ints(lines[1], 3)
    for v in (xs, ys, t):
        if not 1 <= v <= 10**16: raise ValueError("xs/ys/t out of range")
