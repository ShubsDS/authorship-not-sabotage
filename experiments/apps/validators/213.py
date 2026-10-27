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
    n, m = _ints(L[0], 2, "n m")
    _rng(n, 1, 100, "n")
    _rng(m, 0, 100, "m")
    if len(L) != m + 1:
        raise ValueError("line count != m+1")
    mem = []
    ks = set()
    for i in range(m):
        k, f = _ints(L[1 + i], 2, f"memory {i+1}")
        _rng(k, 1, 100, "k")
        _rng(f, 1, 100, "f")
        if k in ks:
            raise ValueError("duplicate k")
        ks.add(k)
        mem.append((k, f))
    # any per-floor count >= 100 behaves like 100 for flats <= 100
    ok = any(all((k - 1) // c + 1 == f for k, f in mem) for c in range(1, 101))
    if not ok:
        raise ValueError("memory is self-contradictory")
