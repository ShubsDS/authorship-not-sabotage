WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    t = lines[0].split()
    if len(t) != 2: raise ValueError("expected n m")
    n, m = int(t[0]), int(t[1])
    if not 2 <= n <= m <= 2 * 10**5: raise ValueError("need 2<=n<=m<=2e5")
