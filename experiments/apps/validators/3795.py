WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 3: raise ValueError("expected three lines")
    v = []
    for ln in lines:
        t = ln.split()
        if len(t) != 1: raise ValueError("one integer per line")
        v.append(int(t[0]))
    n, d, e = v
    if not 1 <= n <= 10**8: raise ValueError("n out of range")
    if not 30 <= d <= 100: raise ValueError("d out of range")
    if not 30 <= e <= 100: raise ValueError("e out of range")
