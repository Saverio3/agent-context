from ..core import STUB, salient
from . import m06_echo
NAME = "Full stack (collapse + echo + old agent notes shortened)"
LOSSLESS = False
DESCRIPTION = ("Version collapse and echo retention, plus the agent's own messages older than the last 3 steps "
               "are cut to their first 2 sentences (its decisions, not its long reasoning). Everything stored.")
KEEP = 3

def _short(c, n=2):
    parts = c.replace("\n", " ").split(". ")
    return c if len(parts) <= n else ". ".join(parts[:n]) + ". [rest stored]"

def policy(ctx):
    base = m06_echo.policy(ctx)
    asst = [i for i, (r, _) in enumerate(ctx) if r == "assistant"]
    old = set(asst[:-KEEP]) if len(asst) > KEEP else set()
    return [_short(c) if i in old else v for i, (v, (_, c)) in enumerate(zip(base, ctx))]
