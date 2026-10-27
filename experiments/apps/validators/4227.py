WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 2: raise ValueError("expected N M")
    n, m = int(t[0]), int(t[1])
    if not 2 <= n <= 8: raise ValueError("N out of range")
    if not 0 <= m <= n * (n - 1) // 2: raise ValueError("M out of range")
    if len(lines) != m + 1: raise ValueError("expected M edges")
    seen = set()
    for ln in lines[1:]:
        r = ln.split()
        if len(r) != 2: raise ValueError("expected a b")
        a, b = int(r[0]), int(r[1])
        if not 1 <= a < b <= n: raise ValueError("need 1<=a<b<=N")
        if (a, b) in seen: raise ValueError("double edge")
        seen.add((a, b))
