from ..core import STUB
from . import m02_collapse
NAME = "Tree memory (fractal idea, offline proxy)"
LOSSLESS = False
DESCRIPTION = ("Recent 3 steps are leaves in full. Older steps fold into a branch line each: the agent's own first "
               "sentence for that step plus the first line of its output; full leaves stay in storage. "
               "A real version would use an AI to write branch summaries; this proxy needs no AI.")
KEEP = 3

def _first_line(s, n=160):
    for line in s.splitlines():
        if line.strip():
            return line.strip()[:n]
    return ""

def policy(ctx):
    base = m02_collapse.policy(ctx)
    asst = [i for i, (r, _) in enumerate(ctx) if r == "assistant"]
    cutoff = asst[-KEEP] if len(asst) >= KEEP else 0
    out = []
    for i, (v, (r, c)) in enumerate(zip(base, ctx)):
        if i >= cutoff or r in ("system", "task"):
            out.append(v)
        elif r == "assistant":
            out.append(c if len(c) < 400 else _first_line(c, 300))
        else:  # tool
            out.append(STUB if v is STUB else "[out] " + _first_line(c))
    return out
