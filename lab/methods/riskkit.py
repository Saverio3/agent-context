"""Shared building blocks for the risk-reduction methods (m16+). Not a method itself."""
import re
from ..core import STUB, salient
from . import m02_collapse

ERR = re.compile(r"Error|Exception|Traceback|FAIL|failed|assert", re.I)


def first(s, n=160):
    return next((l.strip()[:n] for l in s.splitlines() if l.strip()), "")


def echo_lines(c, echoed, maxl):
    return [l for l in c.splitlines()[1:] if salient(l) & echoed][:maxl]


def cap(c, head=60, tail=40):
    lines = c.splitlines()
    if len(lines) <= head + tail + 20:
        return c
    return "\n".join(lines[:head] + [f"[... {len(lines) - head - tail} lines stored ...]"] + lines[-tail:])


def fold(ctx, *, keep=3, mid=None, mid_lines=20, far_lines=8, working_set=0, keep_notes=False,
         sticky=0, keep_errors=False, cap_fresh=True):
    """Generalised tree + echo.
    keep        : last N agent steps stay in full
    mid         : steps aged keep..mid keep up to mid_lines echoed lines (gradual decay); older keep far_lines
    working_set : the latest view of any file touched in the last N steps stays in full
    keep_notes  : never shorten the agent's own messages
    sticky      : an item whose names the agent used in one of its last `sticky` messages is unfolded
    keep_errors : error/traceback lines are never hidden
    """
    base = m02_collapse.policy(ctx)
    asst = [i for i, (r, _) in enumerate(ctx) if r == "assistant"]
    step_of = {}
    s = 0
    for i, (r, _) in enumerate(ctx):
        if r == "assistant":
            s += 1
        step_of[i] = s
    now = s
    echoed = set()
    for r, c in ctx:
        if r in ("assistant", "task"):
            echoed |= salient(c)
    hot_files = set()
    if working_set:
        for i, (r, c) in enumerate(ctx):
            if r == "tool" and now - step_of[i] < working_set:
                k = m02_collapse._key(c)
                if k:
                    hot_files.add(k)
    recent = set()
    if sticky:
        for i in asst[-sticky:]:
            recent |= salient(ctx[i][1])
    out = []
    for i, (v, (r, c)) in enumerate(zip(base, ctx)):
        age = now - step_of[i]
        if r in ("system", "task") or age < keep:
            out.append(cap(v) if (cap_fresh and r == "tool" and v is c) else v)
            continue
        if r == "assistant":
            out.append(c if (keep_notes or len(c) < 400) else first(c, 300))
            continue
        if v is STUB:                      # superseded copy: newest copy is visible elsewhere
            out.append(STUB)
            continue
        if hot_files and m02_collapse._key(c) in hot_files:
            out.append(cap(c))
            continue
        if sticky and len(salient(c) & recent) >= 3:
            out.append(cap(c))
            continue
        n = mid_lines if (mid and age < mid) else far_lines
        body = ["[out] " + first(c)] + echo_lines(c, echoed, n)
        if keep_errors:
            body += [l for l in c.splitlines() if ERR.search(l) and l not in body][:6]
        out.append("\n".join(body + ["[full output stored]"]))
    return out
