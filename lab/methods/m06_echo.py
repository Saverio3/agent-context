from ..core import salient
from . import m02_collapse
NAME = "Echo retention (new)"
LOSSLESS = False
DESCRIPTION = ("Uses the agent's own words as the relevance signal. In tool outputs older than the last 3, keep "
               "only lines containing something the agent or the task has already mentioned (names, paths, "
               "numbers, error types), plus the first 2 lines. Everything else is stored, not shown. "
               "No AI call; decided from the past only.")
KEEP, HEAD = 3, 2

def policy(ctx):
    base = m02_collapse.policy(ctx)
    echoed = set()
    for r, c in ctx:
        if r in ("assistant", "task"):
            echoed |= salient(c)
    tool_idx = [i for i, (r, _) in enumerate(ctx) if r == "tool"]
    old = set(tool_idx[:-KEEP]) if len(tool_idx) > KEEP else set()
    out = []
    for i, (v, (r, c)) in enumerate(zip(base, ctx)):
        if i not in old or v is not c:
            out.append(v); continue
        lines = c.splitlines()
        kept = lines[:HEAD] + [l for l in lines[HEAD:] if salient(l) & echoed]
        out.append(c if len(kept) == len(lines) else "\n".join(kept + [f"[{len(lines)-len(kept)} lines stored]"]))
    return out
