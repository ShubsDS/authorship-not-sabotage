WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 2: raise ValueError("expected two lines")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line n")
    n = int(t[0])
    if not 3 <= n <= 50: raise ValueError("n out of range")
    a = [int(x) for x in lines[1].split()]
    if len(a) != n: raise ValueError("expected n numbers")
    if any(not 1 <= x <= 1000 for x in a): raise ValueError("t_i out of range")
