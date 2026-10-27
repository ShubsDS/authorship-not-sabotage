WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 2: raise ValueError("expected two lines")
    t = lines[0].split()
    if len(t) != 2: raise ValueError("expected n w")
    n, w = int(t[0]), int(t[1])
    if not (1 <= n <= 1000 and 1 <= w <= 10**9): raise ValueError("n/w out of range")
    a = [int(x) for x in lines[1].split()]
    if len(a) != n: raise ValueError("expected n numbers")
    if any(not -10**6 <= x <= 10**6 for x in a): raise ValueError("a_i out of range")
