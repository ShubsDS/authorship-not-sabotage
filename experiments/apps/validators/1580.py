WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
import re

_INT = re.compile(r"-?(0|[1-9][0-9]*)$")


def _int(tok, lo=None, hi=None, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: not an integer: {tok!r}")
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


def _toks(line, n=None):
    t = line.split(" ") if line else []
    if any(x == "" for x in t):
        raise ValueError("bad spacing")
    if n is not None and len(t) != n:
        raise ValueError(f"expected {n} tokens, got {len(t)}")
    return t


def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    t = _toks(L[0], 2)
    N = _int(t[0], 2, 10**5, "N"); M = _int(t[1], 1, 10**5, "M")
    if len(L) != M + 1: raise ValueError("line count")
    par = list(range(N + 1)); rel = [0] * (N + 1)  # rel = parity relative to parent
    def find(x):
        path = []
        while par[x] != x:
            path.append(x); x = par[x]
        root = x
        # compress, accumulating parity from the top
        acc = 0
        for v in reversed(path):
            acc ^= rel[v]
            rel[v] = acc
            par[v] = root
        return root
    seen = set()
    for i in range(M):
        t = _toks(L[1 + i], 3)
        x = _int(t[0], 1, N, "X"); y = _int(t[1], 1, N, "Y"); z = _int(t[2], 1, 100, "Z")
        if not x < y: raise ValueError("X >= Y")
        if (x, y) in seen: raise ValueError("duplicate pair")
        seen.add((x, y))
        d = z & 1  # parity(A_x) xor parity(A_y) must equal Z mod 2
        rx, ry = find(x), find(y)
        px, py = rel[x] if par[x] != x else 0, rel[y] if par[y] != y else 0
        if rx == ry:
            if px ^ py != d: raise ValueError("contradiction")
        else:
            par[rx] = ry; rel[rx] = px ^ py ^ d
