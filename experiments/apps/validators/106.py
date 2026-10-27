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
    _nlines(L, 2)
    n, m, k = _ints(L[0], 3)
    for v, nm in ((n, "n"), (m, "m"), (k, "k")):
        _rng(v, 1, 1000, nm)
    a, b = _ints(L[1], 2)
    _rng(a, 1, n * m * k, "a")
    _rng(b, 1, n * m * k, "b")
    if a == b:
        raise ValueError("a == b")
