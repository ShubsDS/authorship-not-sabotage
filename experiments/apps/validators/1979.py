WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 3: raise ValueError("expected three lines")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line n")
    n = int(t[0])
    if not 1 <= n <= 2 * 10**5: raise ValueError("n out of range")
    for k in (1, 2):
        p = [int(x) for x in lines[k].split()]
        if len(p) != n: raise ValueError("expected n numbers")
        if sorted(p) != list(range(1, n + 1)): raise ValueError("not a permutation")
