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
    if len(lines) != 2: raise ValueError("expected two lines")
    t = lines[0].split(" ")
    if len(t) != 1: raise ValueError("expected n alone")
    n = _int(t[0])
    if not 1 <= n <= 500: raise ValueError("n out of range")
    a = lines[1].split(" ")
    if len(a) != n: raise ValueError("expected n numbers")
    for x in a:
        if not 1 <= _int(x) <= 10**9: raise ValueError("a_i out of range")
