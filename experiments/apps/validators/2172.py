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

_W = re.compile(r"[a-z]{1,10}")


def validate(s):
    L = _lines(s)
    _need(L, 1)
    n, m = _ints(L[0], 2, "n m")
    _rng(n, 1, 3000, "n")
    _rng(m, 1, 3000, "m")
    if len(L) != m + 2:
        raise ValueError("line count != m+2")
    A, B = set(), set()
    for i in range(m):
        t = L[1 + i].split(" ")
        if len(t) != 2:
            raise ValueError(f"dictionary line {i+1} needs 2 words")
        a, b = t
        for w in t:
            if not _W.fullmatch(w):
                raise ValueError(f"bad word {w!r}")
        if a in A or b in B:
            raise ValueError("word repeated within its language")
        A.add(a)
        B.add(b)
    if A & B:
        raise ValueError("word occurs in both languages")
    c = L[m + 1].split(" ")
    if len(c) != n:
        raise ValueError("lecture must have n words")
    for w in c:
        if not _W.fullmatch(w):
            raise ValueError(f"bad word {w!r}")
        if w not in A:
            raise ValueError(f"lecture word {w!r} not in first language")
