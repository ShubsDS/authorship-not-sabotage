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
    n, T = _ints(lines[0], 2)
    if not 1 <= n <= 100: raise ValueError("n out of range")
    if not 1 <= T <= 10**7: raise ValueError("T out of range")
    if any(not 1 <= v <= 300 for v in _ints(lines[1], n)): raise ValueError("a_i out of range")
