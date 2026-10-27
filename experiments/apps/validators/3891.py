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
    if not L:
        raise ValueError("empty")
    n, m = _ints(L[0], 2)
    _rng(n, 1, 115, "n")
    _rng(m, 1, 115, "m")
    _nlines(L, n + 1)
    cells = []
    for i in range(n):
        row = L[1 + i]
        if len(row) != m or not re.fullmatch(r"[WB]+", row):
            raise ValueError(f"bad row {i + 1}")
        for j, ch in enumerate(row):
            if ch == "B":
                cells.append((i, j))
    if not cells:
        raise ValueError("no black square")
    r0 = min(c[0] for c in cells); r1 = max(c[0] for c in cells)
    c0 = min(c[1] for c in cells); c1 = max(c[1] for c in cells)
    h, w = r1 - r0 + 1, c1 - c0 + 1
    if h != w or h % 2 == 0 or len(cells) != h * w:
        raise ValueError("black cells are not a square of odd side")
