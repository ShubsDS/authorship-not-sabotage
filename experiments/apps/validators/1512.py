WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 2: raise ValueError("expected two lines")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line n")
    n = int(t[0])
    if not 1 <= n <= 10**5: raise ValueError("n out of range")
    p = [int(x) for x in lines[1].split()]
    if len(p) != n: raise ValueError("expected n numbers")
    if sorted(p) != list(range(1, n + 1)): raise ValueError("not a permutation")
