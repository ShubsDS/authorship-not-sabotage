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
    if len(t) != 1: raise ValueError("expected one token")
    y = _int(t[0])
    if not 1000 <= y <= 9000: raise ValueError("y out of range")
    # answer exists guarantee
    z = y + 1
    while len(set(str(z))) != len(str(z)):
        z += 1
        if z > 10**5: raise ValueError("no answer")
