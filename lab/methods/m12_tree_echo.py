from ..core import STUB, salient
from . import m02_collapse
NAME = "Tree + echo (new)"
LOSSLESS = False
DESCRIPTION = ("Tree memory, but each folded old output keeps its first line plus up to 8 lines mentioning things "
               "the agent or task already named, instead of one line only. Aims at tree-level savings with fewer misses.")
KEEP, MAXL = 3, 8

def _first(s, n=160):
    return next((l.strip()[:n] for l in s.splitlines() if l.strip()), "")

def fold(ctx, keep=KEEP, maxl=MAXL):
    base = m02_collapse.policy(ctx)
    asst = [i for i, (r, _) in enumerate(ctx) if r == "assistant"]
    cutoff = asst[-keep] if len(asst) >= keep else 0
    echoed = set()
    for r, c in ctx:
        if r in ("assistant", "task"):
            echoed |= salient(c)
    out = []
    for i, (v, (r, c)) in enumerate(zip(base, ctx)):
        if i >= cutoff or r in ("system", "task"):
            out.append(v)
        elif r == "assistant":
            out.append(c if len(c) < 400 else _first(c, 300))
        elif v is STUB:
            out.append(STUB)
        else:
            hits = [l for l in c.splitlines()[1:] if salient(l) & echoed][:maxl]
            out.append("\n".join(["[out] " + _first(c)] + hits + ["[full output stored]"]))
    return out

def policy(ctx):
    return fold(ctx)
