WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 2: raise ValueError("expected two lines")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line n")
    n = int(t[0])
    if not 2 <= n <= 100000: raise ValueError("n out of range")
    a = [int(x) for x in lines[1].split()]
    if len(a) != n - 1: raise ValueError("expected n-1 numbers")
    if any(not 1 <= x <= n for x in a): raise ValueError("a_i out of range")
    if len(set(a)) != len(a): raise ValueError("a_i not distinct")
