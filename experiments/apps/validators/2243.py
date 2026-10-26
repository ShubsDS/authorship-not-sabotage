WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

import re

_INT_RE = re.compile(r"^-?[0-9]+$")


def _int(tok, what="value"):
    if not _INT_RE.match(tok):
        raise ValueError(f"{what}: {tok!r} is not an integer")
    return int(tok)


def _ints(line, cnt=None, what="line"):
    toks = line.split(" ") if line != "" else []
    if cnt is not None and len(toks) != cnt:
        raise ValueError(f"{what}: expected {cnt} tokens, got {len(toks)}")
    return [_int(t, what) for t in toks]


def _rng(v, lo, hi, what):
    if not lo <= v <= hi:
        raise ValueError(f"{what}={v} not in [{lo}, {hi}]")


def _lines(s, n=None):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    lines = s.split("\n")[:-1]
    if n is not None and len(lines) != n:
        raise ValueError(f"expected {n} lines, got {len(lines)}")
    return lines


def _need(lines, k):
    if len(lines) < k:
        raise ValueError(f"expected at least {k} lines, got {len(lines)}")

def validate(s):
    L = _lines(s)
    _need(L, 2)
    n, k, q = _ints(L[0], 3, "n k q")
    _rng(n, 1, 150000, "n")
    _rng(q, 1, 150000, "q")
    _rng(k, 1, min(6, n), "k")
    if len(L) != q + 2:
        raise ValueError("line count != q+2")
    t = _ints(L[1], n, "t")
    for v in t:
        _rng(v, 1, 10**9, "t_i")
    if len(set(t)) != n:
        raise ValueError("t_i not distinct")
    online = set()
    has2 = False
    for i in range(q):
        ty, idx = _ints(L[2 + i], 2, f"query {i+1}")
        _rng(ty, 1, 2, "type")
        _rng(idx, 1, n, "id")
        if ty == 1:
            if idx in online:
                raise ValueError("friend comes online twice")
            online.add(idx)
        else:
            has2 = True
    if not has2:
        raise ValueError("no query of type 2")
