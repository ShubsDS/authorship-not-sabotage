WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    t = lines[0].split()
    if len(t) != 3: raise ValueError("expected N X T")
    for v in map(int, t):
        if not 1 <= v <= 1000: raise ValueError("value out of range")
