from ..core import salient
NAME = "CEILING: perfect foresight (not buildable)"
LOSSLESS = False
DESCRIPTION = ("Upper bound, for reference only. Instructions and task kept; from every other earlier message keep only "
               "the lines whose names/paths/numbers the agent will actually use later. Shows the most any method could save.")

def policy(ctx, future):
    need = set()
    for r, c in future:
        if r == "assistant":
            need |= salient(c)
    out = []
    for r, c in ctx:
        if r in ("system", "task"):
            out.append(c); continue
        keep = [l for l in c.splitlines() if salient(l) & need]
        out.append(c if len(keep) == len(c.splitlines()) else "\n".join(keep))
    return out
policy.needs_future = True
