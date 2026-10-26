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
    _need(L, 1)
    h, w = _ints(L[0], 2, "h w")
    _rng(h, 1, 500, "h")
    _rng(w, 1, 500, "w")
    _need(L, h + 2)
    for i in range(h):
        row = L[1 + i]
        if len(row) != w or not re.fullmatch(r"[.#]+", row):
            raise ValueError(f"grid row {i+1} invalid")
    (q,) = _ints(L[1 + h], 1, "q")
    _rng(q, 1, 100000, "q")
    if len(L) != h + 2 + q:
        raise ValueError("line count != h+2+q")
    for i in range(q):
        r1, c1, r2, c2 = _ints(L[h + 2 + i], 4, f"query {i+1}")
        _rng(r1, 1, h, "r1")
        _rng(r2, r1, h, "r2")
        _rng(c1, 1, w, "c1")
        _rng(c2, c1, w, "c2")
