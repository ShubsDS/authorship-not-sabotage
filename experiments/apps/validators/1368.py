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
MULTIPLE_ANSWERS = True
UNCHECKED = ['v_i accepted either one per line (as in the format) or all on one line (as in the stored tests)', "A<=B checked: implied by 'at least A and at most B'"]

def validate(s: str) -> None:
    L = _lines(s)
    if len(L) < 2: raise ValueError("too few lines")
    n, a, b = _ints(L[0], 3, name="N A B")
    if not 1 <= n <= 50: raise ValueError("N out of range")
    if not (1 <= a <= n and 1 <= b <= n): raise ValueError("A,B out of range")
    if a > b: raise ValueError("A > B")
    rest = L[1:]
    if len(rest) == 1:
        vals = _ints(rest[0], n, 1, 10**15, "v")
    elif len(rest) == n:
        vals = [_ints(x, 1, 1, 10**15, "v")[0] for x in rest]
    else:
        raise ValueError("bad layout of v_i")
