import re
WHITESPACE_SENSITIVE = False
MULTIPLE_ANSWERS = False
UNCHECKED = []
_S = re.compile(r"[a-z]{5},[a-z]{7},[a-z]{5}")
def validate(s):
    lines = s.split("\n")[:-1]
    if len(lines) != 1: raise ValueError("expected one line")
    if not _S.fullmatch(lines[0]): raise ValueError("bad format")
