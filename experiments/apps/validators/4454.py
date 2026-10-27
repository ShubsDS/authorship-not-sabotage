WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line q")
    q = int(t[0])
    if not 1 <= q <= 100: raise ValueError("q out of range")
    if len(lines) != 2 * q + 1: raise ValueError("expected 2q lines")
    for i in range(q):
        h = lines[1 + 2 * i].split()
        if len(h) != 1: raise ValueError("expected n")
        n = int(h[0])
        if not 1 <= n <= 100: raise ValueError("n out of range")
        a = [int(x) for x in lines[2 + 2 * i].split()]
        if len(a) != n: raise ValueError("expected n numbers")
        if any(not 1 <= x <= 10**7 for x in a): raise ValueError("a_i out of range")
