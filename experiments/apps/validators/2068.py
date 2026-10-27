import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_N = re.compile(r"[A-Za-z0-9]{2,24}")
def validate(s):
    lines = s.split("\n")[:-1]
    if not lines: raise ValueError("empty")
    t = lines[0].split()
    if len(t) != 1: raise ValueError("first line n")
    n = int(t[0])
    if not 1 <= n <= 200: raise ValueError("n out of range")
    if len(lines) != n + 1: raise ValueError("expected n reposts")
    have = {"polycarp"}
    for ln in lines[1:]:
        w = ln.split(" ")
        if len(w) != 3 or w[1] != "reposted": raise ValueError("bad repost line")
        a, b = w[0], w[2]
        if not _N.fullmatch(a) or not _N.fullmatch(b): raise ValueError("bad name")
        a, b = a.lower(), b.lower()
        if a in have: raise ValueError("name1 already had the joke")
        if b not in have: raise ValueError("name2 did not have the joke")
        have.add(a)
