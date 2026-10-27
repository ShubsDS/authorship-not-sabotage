import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_INT = re.compile(r"-?(0|[1-9][0-9]*)")
def _int(tok, name="value"):
    if not _INT.fullmatch(tok):
        raise ValueError(f"{name}: bad integer token {tok!r}")
    return int(tok)
def _lines(s):
    return s.split("\n")[:-1]
def _toks(line, k=None, what="line"):
    t = line.split(" ") if line else []
    if k is not None and len(t) != k:
        raise ValueError(f"{what}: expected {k} tokens, got {len(t)}")
    return t
def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of [{lo}, {hi}]")

def validate(s):
    L = _lines(s)
    if len(L) != 2: raise ValueError("expected 2 lines")
    _toks(L[0], 1); n = _int(L[0], "n")
    _rng(n, 1, 55, "n")
    t = L[1]
    if not re.fullmatch(r"[a-z]+", t): raise ValueError("t not lowercase letters")
    if len(t) != n: raise ValueError("len(t) != n")
    # answer exists: n = m(m+1)/2 with 1<=m<=10, and block i (length i) is one repeated letter
    pos, m = 0, 0
    while pos < n:
        m += 1
        blk = t[pos:pos + m]
        if len(blk) != m: raise ValueError("n is not triangular; no decryption exists")
        if len(set(blk)) != 1: raise ValueError(f"block {m} not a single repeated letter")
        pos += m
    if m > 10: raise ValueError("decrypted length > 10")
