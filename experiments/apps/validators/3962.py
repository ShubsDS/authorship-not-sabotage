WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line n")
    n = int(t[0])
    if not 1 <= n <= 10**5: raise ValueError("n out of range")
    if len(lines) != n + 1: raise ValueError("expected n lines")
    for ln in lines[1:]:
        r = ln.split()
        if len(r) != 2: raise ValueError("expected l r")
        a, b = int(r[0]), int(r[1])
        if not (0 <= a <= 10**9 and 0 <= b <= 10**9): raise ValueError("l_i/r_i out of range")
