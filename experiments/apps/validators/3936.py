WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []

import re
_INT = re.compile(r"-?[0-9]+\Z")


def _int(tok, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: not an integer: {tok[:20]!r}")
    return int(tok)


def _lines(s):
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return s.split("\n")[:-1]


def _ints(line, cnt=None, name="line"):
    toks = line.split()
    if cnt is not None and len(toks) != cnt:
        raise ValueError(f"{name}: expected {cnt} tokens, got {len(toks)}")
    return [_int(t, name) for t in toks]


def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of range [{lo}, {hi}]")


def _nlines(lines, k):
    if len(lines) != k:
        raise ValueError(f"expected {k} lines, got {len(lines)}")


def validate(s):
    L = _lines(s)
    _nlines(L, 3)
    (N,) = _ints(L[0], 1)
    _rng(N, 1, 52, "N")
    S = L[1:]
    for t in S:
        if len(t) != N or not re.fullmatch(r"[a-zA-Z]+", t):
            raise ValueError("bad row string")
    pos = {}
    for i in range(2):
        for j in range(N):
            pos.setdefault(S[i][j], []).append((i, j))
    for ch, p in pos.items():
        if len(p) != 2:
            raise ValueError(f"letter {ch} covers {len(p)} cells")
        (a, b), (c, d) = p
        if abs(a - c) + abs(b - d) != 1:
            raise ValueError(f"letter {ch} cells not adjacent")
