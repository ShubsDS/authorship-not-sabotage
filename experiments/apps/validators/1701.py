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


_OCT = r"(0|[1-9][0-9]{0,2})"
_IP = re.compile(r"%s\.%s\.%s\.%s" % (_OCT, _OCT, _OCT, _OCT))

def _ip(x):
    if not _IP.fullmatch(x): raise ValueError(f"bad ip {x!r}")
    if any(int(p) > 255 for p in x.split(".")): raise ValueError(f"ip octet > 255: {x!r}")
    return x

def validate(s):
    L = _lines(s)
    if not L: raise ValueError("empty")
    t = _toks(L[0], 2)
    n = _int(t[0], 1, 1000, "n"); m = _int(t[1], 1, 1000, "m")
    if len(L) != 1 + n + m: raise ValueError("line count")
    ips = set()
    for i in range(n):
        name, ip = _toks(L[1 + i], 2)
        if not re.fullmatch(r"[a-z]{1,10}", name): raise ValueError("bad name")
        _ip(ip)
        if ip in ips: raise ValueError("duplicate ip")
        ips.add(ip)
    for i in range(m):
        cmd, ip = _toks(L[1 + n + i], 2)
        if not re.fullmatch(r"[a-z]{1,10}", cmd): raise ValueError("bad command")
        if not ip.endswith(";"): raise ValueError("missing ;")
        ip = _ip(ip[:-1])
        if ip not in ips: raise ValueError("unknown ip")
