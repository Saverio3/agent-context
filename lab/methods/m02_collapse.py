import re
from ..core import STUB
NAME = "Version collapse"
LOSSLESS = True
DESCRIPTION = ("An older view of a file the agent later re-opened, or an exact repeat of an earlier output, "
               "becomes a pointer. Only superseded copies are hidden; the latest copy is always visible.")
FILE_RE = re.compile(r"\[File: ([^\s\]]+) \(\d+ lines total\)\]|^(?:File|Contents of|cat) ([\w./-]+\.\w+)", re.M)

def _key(c):
    m = FILE_RE.search(c)
    return (m.group(1) or m.group(2)) if m else None

def stale_flags(ctx):
    latest_file, latest_text = {}, {}
    for i, (r, c) in enumerate(ctx):
        if r == "tool":
            k = _key(c)
            if k: latest_file[k] = i
            latest_text[c] = i
    flags = []
    for i, (r, c) in enumerate(ctx):
        k = _key(c) if r == "tool" else None
        stale = r == "tool" and len(c) > 48 and ((k and latest_file[k] != i) or latest_text[c] != i)
        flags.append(bool(stale))
    return flags

def policy(ctx):
    return [STUB if s else c for s, (_, c) in zip(stale_flags(ctx), ctx)]
