WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) < 2: raise ValueError("too few lines")
    t = lines[0].split()
    if len(t) != 2: raise ValueError("expected n m")
    n, m = int(t[0]), int(t[1])
    if not 1 <= n <= 2 * 10**5: raise ValueError("n out of range")
    if not 0 <= m <= 2 * 10**5: raise ValueError("m out of range")
    if len(lines) != m + 2: raise ValueError("expected m offer lines")
    a = [int(x) for x in lines[1].split()]
    if len(a) != n: raise ValueError("expected n numbers")
    if any(not 1 <= x <= 10**12 for x in a): raise ValueError("a_i out of range")
    for ln in lines[2:]:
        r = ln.split()
        if len(r) != 3: raise ValueError("expected x y w")
        x, y, w = map(int, r)
        if not (1 <= x <= n and 1 <= y <= n): raise ValueError("x/y out of range")
        if x == y: raise ValueError("x == y")
        if not 1 <= w <= 10**12: raise ValueError("w out of range")
