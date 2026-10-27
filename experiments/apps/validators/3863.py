WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    t = lines[0].split()
    if len(t) != 2: raise ValueError("expected N K")
    n, k = int(t[0]), int(t[1])
    if not (1 <= n <= 10**9 and 1 <= k <= 10**9): raise ValueError("out of range")
