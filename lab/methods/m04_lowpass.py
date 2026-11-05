from . import m02_collapse
NAME = "Low-pass memory (epicycloid idea)"
LOSSLESS = False
DESCRIPTION = ("Slow layer kept in full: task, instructions, every agent message (its plans and decisions). "
               "Fast layer squeezed, not hidden: tool outputs older than the last 3 keep only their first and "
               "last 6 lines. Built on version collapse.")
KEEP, HEAD = 3, 6

def _squeeze(c):
    lines = c.splitlines()
    if len(lines) <= 2 * HEAD + 1:
        return c
    return "\n".join(lines[:HEAD] + [f"[... {len(lines) - 2*HEAD} lines stored ...]"] + lines[-HEAD:])

def policy(ctx):
    base = m02_collapse.policy(ctx)
    tool_idx = [i for i, (r, _) in enumerate(ctx) if r == "tool"]
    old = set(tool_idx[:-KEEP]) if len(tool_idx) > KEEP else set()
    return [_squeeze(v) if (i in old and v is c) else v for i, (v, (_, c)) in enumerate(zip(base, ctx))]
