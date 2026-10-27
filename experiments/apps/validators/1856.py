import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_P = re.compile(r"[a-z]{1,50}")
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line n")
    n = int(t[0])
    if not 1 <= n <= 2 * 10**5: raise ValueError("n out of range")
    if len(lines) != n + 1: raise ValueError("expected n passwords")
    total = 0
    for w in lines[1:]:
        if not _P.fullmatch(w): raise ValueError("bad password")
        total += len(w)
    if total > 10**6: raise ValueError("total length > 1e6")
