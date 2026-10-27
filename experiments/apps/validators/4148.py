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
    (n,) = _ints(lines[0], 1)
    if not 0 <= n <= 26: raise ValueError("N out of range")
    S = lines[1]
    if not 1 <= len(S) <= 10**4: raise ValueError("|S| out of range")
    if not re.fullmatch(r"[A-Z]+", S): raise ValueError("S not uppercase letters")
