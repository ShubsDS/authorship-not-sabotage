import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_I = re.compile(r"-?[0-9]+")
def _int(x):
    if not _I.fullmatch(x): raise ValueError(f"bad integer {x!r}")
    return int(x)
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    t = lines[0].split(" ")
    if len(t) != 2: raise ValueError("expected two tokens")
    n, b = _int(t[0]), _int(t[1])
    if not 1 <= n <= 10**18: raise ValueError("n out of range")
    if not 2 <= b <= 10**12: raise ValueError("b out of range")
