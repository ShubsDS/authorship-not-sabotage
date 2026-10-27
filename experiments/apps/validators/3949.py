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
    n, m = _ints(lines[0], 2)
    if not (1 <= n <= 1000 and 1 <= m <= 1000): raise ValueError("n/m out of range")
    if len(lines) != n + 1: raise ValueError("expected n rows")
    for row in lines[1:]:
        if len(row) != m or set(row) - set("#."): raise ValueError("bad row")
