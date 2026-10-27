WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False  # "print any", but positive a_i with n >= 3 are fixed by a_i^2 = M_ij*M_ik/M_jk
UNCHECKED = []

import re
_INT = re.compile(r"-?(0|[1-9][0-9]*)$")


def _int(tok, name="value"):
    if not _INT.match(tok):
        raise ValueError(f"{name}: bad integer token {tok!r}")
    return int(tok)


def _lines(s):
    lines = s.split("\n")
    if not s.endswith("\n"):
        raise ValueError("missing final newline")
    return lines[:-1]


def _ints(line, k=None, name="line"):
    toks = line.split(" ") if line else []
    if k is not None and len(toks) != k:
        raise ValueError(f"{name}: expected {k} tokens, got {len(toks)}")
    return [_int(t, name) for t in toks]


def _rng(v, lo, hi, name):
    if not lo <= v <= hi:
        raise ValueError(f"{name}={v} out of [{lo}, {hi}]")


from math import isqrt


def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    (n,) = _ints(L[0], 1, "n")
    _rng(n, 3, 1000, "n")
    if len(L) != n + 1: raise ValueError("line count != n+1")
    M = []
    for i in range(n):
        row = _ints(L[1 + i], n, f"row {i+1}")
        for j, v in enumerate(row):
            if i == j:
                if v != 0: raise ValueError("diagonal not zero")
            else:
                _rng(v, 1, 10**9, "M_ij")
        M.append(row)
    # guaranteed an answer exists: M_ij = a_i a_j with positive integers a
    num = M[0][1] * M[0][2]
    if num % M[1][2]: raise ValueError("no valid array")
    sq = num // M[1][2]
    a1 = isqrt(sq)
    if a1 * a1 != sq or a1 < 1: raise ValueError("no valid array")
    a = [a1]
    for j in range(1, n):
        if M[0][j] % a1: raise ValueError("no valid array")
        a.append(M[0][j] // a1)
    for i in range(n):
        ai = a[i]; row = M[i]
        for j in range(n):
            if i != j and row[j] != ai * a[j]:
                raise ValueError(f"no valid array (M[{i+1}][{j+1}])")
