import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_N = re.compile(r"[a-z]{1,10}")
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line N")
    n = int(t[0])
    if not 1 <= n <= 100: raise ValueError("N out of range")
    if len(lines) != n + 1: raise ValueError("expected N cheeses")
    names = set()
    for ln in lines[1:]:
        w = ln.split(" ")
        if len(w) != 2: raise ValueError("expected name type")
        if not _N.fullmatch(w[0]): raise ValueError("bad name")
        if w[1] not in ("soft", "hard"): raise ValueError("bad type")
        if w[0] in names: raise ValueError("duplicate name")
        names.add(w[0])
