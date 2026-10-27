WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def _len(x):
    return 1 if x <= 1 else 2 * _len(x // 2) + 1
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    t = lines[0].split()
    if len(t) != 3: raise ValueError("expected n l r")
    n, l, r = map(int, t)
    if not 0 <= n < 2**50: raise ValueError("n out of range")
    if l < 1 or r < 1: raise ValueError("l, r must be >= 1")
    if not 0 <= r - l <= 10**5: raise ValueError("r-l out of range")
    if r > _len(n): raise ValueError("r exceeds final list length")
