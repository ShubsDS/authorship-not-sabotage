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
    n, k = _ints(L[0], 2)
    _rng(n, 1, 100, "N")
    _rng(k, 1, 100, "K")
    _nlines(L, 1 + 2 * k)
    for i in range(k):
        (d,) = _ints(L[1 + 2 * i], 1)
        _rng(d, 1, n, "d_i")
        A = _ints(L[2 + 2 * i], d)
        for x in A:
            _rng(x, 1, n, "A")
        for u, v in zip(A, A[1:]):
            if not u < v:
                raise ValueError("A not strictly increasing")
