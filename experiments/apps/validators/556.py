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
    if len(t) != 3: raise ValueError("expected three tokens")
    l, r, k = map(_int, t)
    if not 1 <= l <= r <= 10**18: raise ValueError("need 1<=l<=r<=1e18")
    if not 2 <= k <= 10**9: raise ValueError("k out of range")
