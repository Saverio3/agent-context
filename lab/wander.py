"""How much do agents wander? (the map-search question)

For each run, every tool output is put in one bucket:
  on-path view   : a look at a file the agent finally changed
  off-path view  : a look at a file it never changed (possible wrong turn)
  search         : grep/find/ls/search results
  run/test       : running code or tests
  edit           : output of an edit
  other

"Changed files" come from the run's final patch (diff), or, if missing, from edit confirmations.
Then: what if the off-path views and the searches that never pointed at a changed file had been
skipped (with the agent step that asked for them)? We re-count the whole re-read cost without
them. That is an upper bound on what better 'sense of direction' could save: some off-path
reading is genuinely needed to understand the code.

python -m lab.wander --jsonl data/nebius.jsonl --out results/nebius
"""
import argparse
import json
import os
import re
import statistics

from .core import toks
from .methods.m02_collapse import _key

DIFF = re.compile(r"^diff --git a/(\S+) b/", re.M)
EDITED = re.compile(r"(?:file|File) (/[\w./-]+\.\w+) (?:has been edited|was created|created successfully)")
SEARCH = re.compile(r"^(Found \d+ match|No matches found|Directory|\./|find |grep )|matches for \"", re.M)
RUN = re.compile(r"Traceback|passed|failed|Error|Exception|^\$ python|OK$", re.M)
BUCKETS = ["on-path view", "off-path view", "search (hit)", "search (miss)", "run/test", "edit", "other"]


def _match(path, changed):
    path = path.lstrip("/")
    return any(path.endswith(c) or c.endswith(path) for c in changed)


def classify(ms, patch):
    changed = set(DIFF.findall(patch or ""))
    if not changed:
        for r, c in ms:
            if r == "tool":
                changed |= {m.lstrip("/") for m in EDITED.findall(c)}
    labels = []
    for r, c in ms:
        if r != "tool":
            labels.append(None); continue
        k = _key(c)
        if "has been edited" in c or "File updated" in c:
            labels.append("edit")
        elif k:
            labels.append("on-path view" if _match(k, changed) else "off-path view")
        elif SEARCH.search(c[:400]):
            hit = any(c.find(x.split("/")[-1]) >= 0 for x in changed)
            labels.append("search (hit)" if hit else "search (miss)")
        elif RUN.search(c):
            labels.append("run/test")
        else:
            labels.append("other")
    return labels, changed


def reread_cost(ms, keep):
    total = 0
    kept = [m for m, k in zip(ms, keep) if k]
    for t, (r, _) in enumerate(kept):
        if r == "assistant":
            total += sum(toks(c) for _, c in kept[:t])
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl")
    ap.add_argument("--limit", type=int, default=3000)
    ap.add_argument("--out")
    a = ap.parse_args()
    share = {b: 0 for b in BUCKETS}
    steps = {b: 0 for b in BUCKETS}
    base_all = cut_all = 0
    per_run, by_solved = [], {True: [], False: []}
    n = with_patch = 0
    with open(a.jsonl) as f:
        for line in f:
            d = json.loads(line)
            from .core import _norm_role
            ms, seen = [], False
            for role, text in d["messages"]:
                role, seen = _norm_role(role, seen)
                ms.append((role, text))
            if sum(r == "assistant" for r, _ in ms) < 4:
                continue
            labels, changed = classify(ms, d.get("patch"))
            if not changed:
                continue
            n += 1; with_patch += bool(d.get("patch"))
            # tokens each tool output costs over the run = its size x number of later re-reads
            asst = [i for i, (r, _) in enumerate(ms) if r == "assistant"]
            for i, lab in enumerate(labels):
                if lab:
                    later = sum(1 for j in asst if j > i)
                    share[lab] += toks(ms[i][1]) * later
                    steps[lab] += 1
            # counterfactual: drop wandering outputs and the agent message that asked for them
            keep = [True] * len(ms)
            for i, lab in enumerate(labels):
                if lab in ("off-path view", "search (miss)"):
                    keep[i] = False
                    if i > 0 and ms[i - 1][0] == "assistant" and i - 1 != asst[-1]:
                        keep[i - 1] = False
            b, c = reread_cost(ms, [True] * len(ms)), reread_cost(ms, keep)
            base_all += b; cut_all += c
            per_run.append(1 - c / b if b else 0)
            if d.get("solved") in (True, False):
                by_solved[d["solved"]].append(1 - c / b if b else 0)
            if n >= a.limit:
                break
    S = sum(share.values()) or 1
    St = sum(steps.values()) or 1
    lines = [f"# Wandering — {n} runs with known changed files ({with_patch} from the final patch)", "",
             "| What the agent was doing | Share of tool steps | Share of tokens re-read from tool outputs |",
             "|---|---|---|"]
    lines += [f"| {b} | {steps[b] / St:.1%} | {share[b] / S:.1%} |" for b in BUCKETS]
    lines += ["", f"**If off-path views and searches that found nothing relevant were skipped** (with the step that "
              f"asked for them): total re-read tokens fall by **{1 - cut_all / base_all:.1%}** "
              f"(median run {statistics.median(per_run):.1%}). Upper bound: some off-path reading is needed.", ""]
    for k, v in by_solved.items():
        if v:
            lines.append(f"- {'Solved' if k else 'Unsolved'} runs: {len(v)}, median wandering saving {statistics.median(v):.1%}")
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "WANDERING.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
