WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 2: raise ValueError("first line needs n m")
    n, m = int(t[0]), int(t[1])
    if not (1 <= n <= 100 and 1 <= m <= 100): raise ValueError("n/m out of range")
    if len(lines) != m + 1: raise ValueError("expected m rows")
    total = 0
    for i in range(m):
        r = lines[1 + i].split()
        if len(r) != n: raise ValueError(f"row {i} needs n numbers")
        for x in r:
            v = int(x)
            if not 0 <= v <= 10**9: raise ValueError("a_ij out of range")
            total += v
    if total > 10**9: raise ValueError("total votes exceed 1e9")
