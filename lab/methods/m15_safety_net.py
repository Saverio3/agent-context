import re
from ..core import STUB, salient
from . import m14_tree_echo_cap
NAME = "Tree + cap + safety net (new)"
LOSSLESS = False
DESCRIPTION = ("Tree + echo + cap, plus two guards: (1) a folded tool output is shown in full again when the agent's "
               "latest message uses at least 4 of its names; (2) error and traceback lines are never hidden.")
ERR = re.compile(r"Error|Exception|Traceback|FAIL|failed|assert", re.I)
PATH = re.compile(r"[\w-]+/[\w./-]+\.\w+|\b[\w-]+\.(?:py|js|ts|java|go|rb|rs|c|cpp|h)\b")

def policy(ctx):
    base = m14_tree_echo_cap.policy(ctx)
    asst = [i for i, (r, _) in enumerate(ctx) if r == "assistant"]
    recent = set()
    for i in asst[-1:]:
        recent |= salient(ctx[i][1])
    out = []
    for v, (r, c) in zip(base, ctx):
        if v is c or r not in ("tool", "assistant"):
            out.append(v); continue
        if r == "tool" and recent and len(salient(c) & recent) >= 4:
            out.append(c); continue
        extra = [l for l in c.splitlines() if ERR.search(l)][:6]
        out.append(v if not extra else "\n".join([v] + extra))
    return out
