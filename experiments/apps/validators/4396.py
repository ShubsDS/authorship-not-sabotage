import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = True  # real-valued output judged with 1e-5 tolerance
UNCHECKED = []
_INT = re.compile(r"-?(0|[1-9][0-9]*)")
def _int(tok, name="value"):
    if not _INT.fullmatch(tok):
        raise ValueError(f"{name}: bad integer {tok!r}")
    return int(tok)
def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of [{lo},{hi}]")
def _lines(s):
    lines = s.split("\n")[:-1]
    return lines
def _toks(line, k, name="line"):
    t = line.split(" ") if line else []
    if k is not None and len(t) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(t)}")
    return t
def _nlines(lines, k):
    if len(lines) != k:
        raise ValueError(f"expected {k} lines, got {len(lines)}")

from fractions import Fraction
def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    n = _int(_toks(L[0], 1)[0]); _rng(n, 2, 10, "N")
    _nlines(L, n + 1)
    for i in range(1, n + 1):
        x, u = _toks(L[i], 2)
        if u == "JPY":
            _rng(_int(x), 1, 10**8, "x_i (JPY)")
        elif u == "BTC":
            if not re.fullmatch(r"(0|[1-9][0-9]*)\.[0-9]{8}", x):
                raise ValueError(f"BTC amount {x!r} not a decimal with 8 digits")
            v = Fraction(x)
            if not Fraction(1, 10**8) <= v <= 100: raise ValueError(f"BTC amount {x} out of range")
        else:
            raise ValueError(f"unit {u!r} not JPY/BTC")
