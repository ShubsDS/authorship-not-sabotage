WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("expected one token")
    n = int(t[0])
    if not 1 <= n <= 10**9: raise ValueError("n out of range")
