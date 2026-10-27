import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_I = re.compile(r"-?[0-9]+")
def _int(x):
    if not _I.fullmatch(x): raise ValueError(f"bad integer {x!r}")
    return int(x)
def _ints(line, k=None):
    t = line.split(" ") if line else []
    if k is not None and len(t) != k: raise ValueError(f"expected {k} tokens, got {len(t)}")
    return [_int(x) for x in t]
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    n, k = _ints(lines[0], 2)
    if not 2 <= n <= 10**9: raise ValueError("n out of range")
    if not 1 <= k <= 50: raise ValueError("k out of range")
    for _ in range(k):
        n = n // 10 if n % 10 == 0 else n - 1
        if n <= 0: raise ValueError("result not positive")
