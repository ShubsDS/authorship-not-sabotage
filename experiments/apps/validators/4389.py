import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_B = re.compile(r"[a-z]{2,100}")
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line t")
    tc = int(t[0])
    if not 1 <= tc <= 1000: raise ValueError("t out of range")
    if len(lines) != tc + 1: raise ValueError("expected t strings")
    for b in lines[1:]:
        if not _B.fullmatch(b): raise ValueError("bad string b")
        if len(b) % 2: raise ValueError("odd length b cannot be built")
        for i in range(1, len(b) - 1, 2):
            if b[i] != b[i + 1]: raise ValueError("b not built by the algorithm")
