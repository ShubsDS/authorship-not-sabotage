import re
_INT = re.compile(r"(0|-?[1-9][0-9]*)$")
def _int(tok, lo=None, hi=None, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: bad integer token {tok!r}")
    v = int(tok)
    if lo is not None and v < lo:
        raise ValueError(f"{name}={v} < {lo}")
    if hi is not None and v > hi:
        raise ValueError(f"{name}={v} > {hi}")
    return v
def _lines(s):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return s.split("\n")[:-1]
def _ints(line, k, lo=None, hi=None, name="value"):
    t = line.split(" ") if line else []
    if len(t) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(t)}")
    return [_int(x, lo, hi, name) for x in t]

WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

def validate(s: str) -> None:
    L = _lines(s)
    if not L: raise ValueError("empty")
    n, q = _ints(L[0], 2, name="n q")
    if not 2 <= n <= 6: raise ValueError("n out of range")
    if not 1 <= q <= 36: raise ValueError("q out of range")
    if len(L) != 1 + q: raise ValueError("wrong number of lines")
    seen = set()
    for x in L[1:]:
        t = x.split(" ")
        if len(t) != 2: raise ValueError("bad op line")
        a, b = t
        if not re.fullmatch(r"[a-f]{2}", a) or not re.fullmatch(r"[a-f]", b): raise ValueError("bad op")
        if a in seen: raise ValueError("duplicate a_i")
        seen.add(a)
