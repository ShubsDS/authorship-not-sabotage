import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
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

def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    n = _int(_toks(L[0], 1)[0]); _rng(n, 2, 3 * 10**5, "n")
    _nlines(L, n + 1)
    a = [_int(t) for t in _toks(L[1], n, "a")]
    for v in a: _rng(v, 0, 2, "a_i")
    if 1 not in a or 2 not in a: raise ValueError("need at least one red and one blue vertex")
    parent = list(range(n + 1))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i in range(2, n + 1):
        v, u = [_int(t) for t in _toks(L[i], 2)]
        _rng(v, 1, n, "v"); _rng(u, 1, n, "u")
        if v == u: raise ValueError("self-loop")
        rv, ru = find(v), find(u)
        if rv == ru: raise ValueError("edges contain a cycle; not a tree")
        parent[rv] = ru
