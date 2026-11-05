"""Shared pieces: load agent runs, replay them under a context policy, score the result.

A run is a list of messages (role, text) with roles: system, task, assistant, tool.
Before every assistant message the model re-reads everything before it. A policy decides
what each earlier message looks like at that moment (full text, a squeezed version, or a
short pointer). Nothing is ever deleted from storage; pointers can be expanded on request.
"""
import functools
import glob
import json
import os
import re

STUB = "[stored: earlier output, retrievable by id]"


def toks(s):
    """Approximate tokens (~4 characters each). Same counter for every method."""
    return max(1, len(s) // 4)


# ---------- loading ----------

def _norm_role(r, seen_task):
    r = (r or "").lower()
    if r in ("assistant", "ai", "model"):
        return "assistant", seen_task
    if r == "system":
        return "system", seen_task
    if r in ("tool", "observation", "function"):
        return "tool", seen_task
    # user: first one is the task, later ones are environment observations
    return ("tool", True) if seen_task else ("task", True)


def load_swe_agent_traj(path):
    d = json.load(open(path))
    out, seen = [], False
    for m in d.get("history", []):
        c = m.get("content", "")
        if isinstance(c, list):
            c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
        role, seen = _norm_role(m.get("role"), seen)
        out.append((role, str(c)))
    return out


def load_local(folder):
    runs = []
    for p in sorted(glob.glob(os.path.join(folder, "**", "*.traj"), recursive=True)):
        ms = load_swe_agent_traj(p)
        if sum(r == "assistant" for r, _ in ms) >= 4:
            runs.append((os.path.relpath(p, folder), ms))
    return runs


def load_jsonl(path, limit=None):
    """Normalised runs written by fetch_data.py: {"id":..., "messages":[[role,text],...]}"""
    runs = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            ms, seen = [], False
            for role, text in d["messages"]:
                role, seen = _norm_role(role, seen)
                ms.append((role, text))
            if sum(r == "assistant" for r, _ in ms) >= 4:
                runs.append((d["id"], ms))
            if limit and len(runs) >= limit:
                break
    return runs


# ---------- scoring ----------

# "Salient" strings an agent might later rely on: identifiers, paths, numbers, error names.
SAL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_./-]*[_./0-9][A-Za-z0-9_./-]*|\b[A-Z][a-z]+Error\b|\b\d{3,}\b")


@functools.lru_cache(maxsize=200000)
def salient(text):
    return frozenset(m for m in SAL_RE.findall(text) if len(m) >= 4)


def replay(ms, policy):
    """Return (tokens re-read over the whole run, references to hidden info, references total).

    A 'reference' is a salient string in an assistant message that already appeared earlier in
    the run. It is a 'miss' if, under the policy, it no longer appears anywhere the model can see
    at that moment: the model used information the policy had hidden from it.
    """
    total = refs = misses = 0
    for t, (role, text) in enumerate(ms):
        if role != "assistant":
            continue
        ctx = ms[:t]
        visible = policy(ctx)
        total += sum(toks(v) for v in visible)
        full_sal, vis_sal = set(), set()
        for (_, c), v in zip(ctx, visible):
            full_sal |= salient(c)
            if v is not c:
                vis_sal |= salient(v)
            else:
                vis_sal |= salient(c)
        used = salient(text) & full_sal
        refs += len(used)
        misses += len(used - vis_sal)
    return total, misses, refs
