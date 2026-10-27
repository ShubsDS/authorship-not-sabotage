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
    if len(L) != 2: raise ValueError("expected 2 lines")
    n, c1, c2 = _ints(L[0], 3, name="n c1 c2")
    if not 1 <= n <= 200000: raise ValueError("n out of range")
    if not (1 <= c1 <= 10**7 and 1 <= c2 <= 10**7): raise ValueError("c out of range")
    t = L[1]
    if len(t) != n or not re.fullmatch(r"[01]+", t): raise ValueError("bad string")
    if "1" not in t: raise ValueError("no adult")
