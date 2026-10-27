WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    t = lines[0].split()
    if len(t) != 3: raise ValueError("expected X Y Z")
    x, y, z = map(int, t)
    for v in (x, y, z):
        if not 1 <= v <= 10**5: raise ValueError("value out of range")
    if y + 2 * z > x: raise ValueError("Y+2Z > X")
