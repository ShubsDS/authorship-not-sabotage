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
    if not lines: raise ValueError("empty")
    t = lines[0].split(" ")
    if len(t) != 1: raise ValueError("expected n alone")
    n = _int(t[0])
    if not 1 <= n <= 100: raise ValueError("n out of range")
    if len(lines) != n + 1: raise ValueError("expected n rows")
    for row in lines[1:]:
        if len(row) != n or set(row) - set("01"): raise ValueError("bad row")
