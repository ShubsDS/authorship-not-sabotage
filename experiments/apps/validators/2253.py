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
    t, = _ints(L[0], 1, 1, 30, "t")
    if len(L) != 1 + t: raise ValueError("wrong number of lines")
    for x in L[1:]:
        if not 1 <= len(x) <= 1000: raise ValueError("bad length")
        if not re.fullmatch(r"[a-z_]+", x): raise ValueError("bad chars")
        if x[0] == "_" or x[-1] == "_" or "__" in x: raise ValueError("bad underscores")
        if not x.endswith(("po", "desu", "masu", "mnida")): raise ValueError("bad suffix")
