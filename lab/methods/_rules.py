"""Forgetting rules for the cross-field round. Each rule(it, C) -> "full" | list of lines to keep."""
import math
import re

from ..core import salient, toks
from ._bk import ERR, SIG, NUM, VITAL, echo

# ---------- brains and animals ----------

def ebbinghaus(it, C):
    """Spaced repetition: an output's lifetime doubles every time the agent mentions its contents."""
    life = 3 * 2 ** min(it.ment, 5)
    return "full" if it.age < life else echo(it, C)

def pheromone(it, C):
    """Ant trails: each line gains scent when the agent mentions its names; scent evaporates 30% per step."""
    keep = []
    for l in it.lines[1:]:
        sc = sum(0.7 ** (C.now - s) for n in salient(l) for s in C.name_steps.get(n, ()) if s > it.first_seen_step)
        if sc > 0.3:
            keep.append(l)
    return keep[:30]

def place_cells(it, C):
    """Cognitive map: for file views keep the map (signatures, imports) + echoed lines; others echo."""
    if it.kind == "file":
        return [l for l in it.lines if SIG.search(l)][:25] + echo(it, C)
    return echo(it, C)

def event_segments(it, C):
    """Event segmentation: keep everything since the last episode boundary (a test run or a new file)."""
    ctx = C.ctx
    boundary_step, seen = 0, set()
    for j, (r, c) in enumerate(ctx):
        if r == "tool":
            from . import m02_collapse
            k = m02_collapse._key(c)
            if (k and k not in seen) or re.search(r"passed|failed|Traceback", c):
                boundary_step = C.step_of[j]
            if k: seen.add(k)
    return "full" if it.first_seen_step >= boundary_step - 1 else echo(it, C)

def amygdala(it, C):
    """Emotional tagging: lines that were surprising when they arrived (brand-new names, errors) are kept."""
    fs = C.first_seen()
    keep = [l for l in it.lines[1:] if ERR.search(l) or any(fs.get(n) == it.first_seen_step for n in salient(l))]
    return keep[:20] + echo(it, C, 4)

def predictive_coding(it, C):
    """Keep only lines that were not predictable: drop any line already seen earlier in the run."""
    seen = set()
    for j, (_, c) in enumerate(C.ctx[: it.i]):
        seen.update(l.strip() for l in c.splitlines() if len(l.strip()) > 15)
    new = [l for l in it.lines[1:] if l.strip() not in seen]
    return new[:40] if len(new) < 0.5 * len(it.lines) else echo(it, C, 15)

def memory_palace(it, C):
    """Method of loci: per file, one card of all echoed lines across every view of that file."""
    if it.kind != "file":
        return echo(it, C)
    from . import m02_collapse
    card = []
    for _, c in C.ctx:
        if m02_collapse._key(c) == it.file:
            card += [l for l in c.splitlines() if salient(l) & C.echoed]
    return list(dict.fromkeys(card))[:20]

def matriarch(it, C):
    """Goal anchoring: lines sharing names with the original task are kept like water-hole locations."""
    return [l for l in it.lines[1:] if salient(l) & C.task][:15] + echo(it, C)

def replay(it, C):
    """Hippocampal replay: every 5 steps the most-mentioned outputs are replayed (kept full) until next replay."""
    return "full" if it.ment >= 3 and (C.now - it.last_ment) <= 5 else echo(it, C)

def sleep_consolidation(it, C):
    """Sleep: older outputs keep only lines whose names recur in 2+ messages (the gist that repeats)."""
    return [l for l in it.lines[1:] if any(C.df[n] >= 2 for n in salient(l) & C.echoed)][:20]

def synaptic_tagging(it, C):
    """Tag & capture: outputs the agent used within 2 steps of seeing them stay full for 12 steps."""
    early = any(it.first_seen_step < s <= it.first_seen_step + 2 for n in salient(it.c) for s in C.name_steps.get(n, ()))
    return "full" if early and it.age < 12 else echo(it, C)

def chunking(it, C):
    """Miller's 7 chunks: only the 7 most-mentioned old outputs keep detail; the rest one line."""
    from ._bk import Ctx
    scores = []
    for j, (r, c) in enumerate(C.ctx):
        if r == "tool" and C.now - C.step_of[j] >= 3:
            scores.append(C.mentions_after(salient(c), C.step_of[j]))
    top = sorted(scores, reverse=True)[:7]
    return echo(it, C, 20) if top and it.ment >= top[-1] and it.ment > 0 else []

def reconsolidation(it, C):
    """Recalled memories become editable again: an output mentioned in the last 3 steps is shown full."""
    return "full" if it.last_ment >= C.now - 3 and it.last_ment > it.first_seen_step else echo(it, C)

def elephant_landmarks(it, C):
    """Elephant water holes: keep numbered locations (file line numbers) the agent ever referred to."""
    nums = {n for n in C.echoed if n.isdigit()}
    return [l for l in it.lines if NUM.match(l) and l.split(":")[0].strip().lstrip("|") in nums][:20] + echo(it, C)

def sparse_coding(it, C):
    """Sparse coding: keep the most informative 15% of lines (rare names), drop boilerplate."""
    sc = sorted(((C.idf(l), k) for k, l in enumerate(it.lines[1:])), reverse=True)
    k = max(3, int(0.15 * len(sc)))
    keep = sorted(j for _, j in sc[:k])
    return [it.lines[1:][j] for j in keep]

# ---------- medicine ----------

def triage(it, C):
    """ESI triage: errors stay full for 10 steps; test/diff outputs keep 20 lines; files 8; rest one line."""
    if it.kind == "error":
        return "full" if it.age < 10 else [l for l in it.lines if ERR.search(l)][:10] + echo(it, C)
    if re.search(r"passed|failed|^[+-]", it.c, re.M):
        return echo(it, C, 20)
    return echo(it, C) if it.kind == "file" else echo(it, C, 3)

def soap(it, C):
    """Problem-oriented record: keep only 'objective findings' (vital signs): errors, results, diffs, numbers."""
    return [l for l in it.lines[1:] if VITAL.search(l)][:20] + echo(it, C)

def half_life(it, C):
    """Drug half-life per tissue: each kind of output has its own lifetime (files 10, errors 8, search 2, other 3)."""
    life = {"file": 10, "error": 8, "search": 2}.get(it.kind, 3)
    return "full" if it.age < life else echo(it, C)

# ---------- computing / data engineering ----------

def arc_cache(it, C):
    """Adaptive replacement cache: keep full if recently OR frequently used (top by recency+frequency)."""
    rec = 1.0 / (1 + C.now - max(it.last_ment, it.first_seen_step))
    return "full" if rec > 0.25 or it.ment >= 4 else echo(it, C)

def knapsack(it, C):
    """Value density: keep full if (mentions+1)/(age+1) per 1k tokens beats a fixed bar."""
    v = (it.ment + 1) / (it.age + 1) / max(0.2, toks(it.c) / 1000)
    return "full" if v > 0.5 else echo(it, C)

def lsm_tiers(it, C):
    """LSM-tree compaction: tier 1 (3-8 steps) 20 lines, tier 2 (8-20) 8 lines, tier 3 (20+) 2 lines."""
    n = 20 if it.age < 8 else 8 if it.age < 20 else 2
    return echo(it, C, n)

def radiology_window(it, C):
    """Windowing: around every echoed line keep 2 lines either side (context, not just the hit)."""
    idx = [k for k, l in enumerate(it.lines) if salient(l) & C.echoed]
    keep = sorted({j for k in idx for j in range(k - 2, k + 3) if 0 < j < len(it.lines)})
    return [it.lines[j] for j in keep][:40]

def file_delta(it, C):
    """Delta encoding: show a file view as only the lines that differ from the agent's previous view."""
    if it.kind != "file":
        return echo(it, C)
    from . import m02_collapse
    prev = None
    for _, c in C.ctx[: it.i]:
        if m02_collapse._key(c) == it.file:
            prev = c
    if prev is None:
        return echo(it, C, 15)
    old = set(prev.splitlines())
    return [l for l in it.lines if l not in old][:30] + echo(it, C, 4)

# ---------- space / control ----------

def progressive(it, C):
    """Progressive transmission: each old output gets a line allowance proportional to its value."""
    allow = int(4 + 6 * it.ment)
    sc = sorted(((len(salient(l) & C.echoed) + 0.1 * C.idf(l), k) for k, l in enumerate(it.lines[1:])), reverse=True)
    return [it.lines[1:][j] for j in sorted(j for _, j in sc[:allow])]

def controller(it, C):
    """Feedback control: the keep window grows by 2 every time the agent recently needed folded content."""
    misses = sum(1 for s in range(max(1, C.now - 8), C.now + 1)
                 if any(t == s for n in salient(it.c) for t in C.name_steps.get(n, ())))
    return "full" if it.age < 3 + 2 * min(misses, 5) else echo(it, C)

def store_forward(it, C):
    """Store-and-forward downlink: errors and edits first; everything else only its echoed headline lines."""
    if it.kind == "error" or "edited" in it.c:
        return echo(it, C, 25) + [l for l in it.lines if ERR.search(l)][:5]
    return echo(it, C, 5)

# ---------- statistics ----------

def exp_decay(it, C):
    """Exponential forgetting: keep full while exp(-age/6)*(1+mentions) > 0.5."""
    return "full" if math.exp(-it.age / 6) * (1 + it.ment) > 0.5 else echo(it, C)

PRIOR = {"file": (2, 40), "error": (2, 60), "search": (1, 200), "other": (1, 150)}

def bayes(it, C):
    """Beta-Binomial: prior chance an output is needed again (by kind), updated by the agent's mentions."""
    a, b = PRIOR[it.kind]
    p = (a + it.ment) / (a + b + max(1, it.age))
    return "full" if p > 0.08 else echo(it, C)

# ---------- our own ----------

def spreading_activation(it, C):
    """Associative memory: keep lines with echoed names AND lines with names that co-occur with them."""
    assoc = set()
    for l in it.lines:
        s = salient(l)
        if s & C.echoed:
            assoc |= s
    return [l for l in it.lines[1:] if salient(l) & (C.echoed | assoc)][:25]

def ensemble_vote(it, C):
    """Keep a line when at least 2 of 3 independent rules keep it (echo, sparse coding, pheromone)."""
    votes = {}
    for rule in (lambda: echo(it, C, 1000), lambda: sparse_coding(it, C), lambda: pheromone(it, C)):
        for l in rule() or []:
            votes[l] = votes.get(l, 0) + 1
    return [l for l in it.lines[1:] if votes.get(l, 0) >= 2][:30]

def mask_k(k):
    def r(it, C):
        return "full" if it.age < k else []
    return r
