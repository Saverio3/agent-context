"""Run every method in lab/methods on a set of agent runs and write results/SUMMARY.md.

Usage:
  python -m lab.run --local data/local                 # the 22 sample runs in the repo
  python -m lab.run --jsonl data/runs.jsonl --limit 2000
"""
import argparse
import csv
import importlib
import os
import pkgutil
import statistics
from multiprocessing import Pool

from . import core, methods

ALWAYS = ("m00_", "m01_", "m18_")


def pick(prefixes):
    names = [m.name for m in pkgutil.iter_modules(methods.__path__)
             if m.name[:1] in prefixes or m.name.startswith(ALWAYS)]
    return [importlib.import_module(f"lab.methods.{n}") for n in sorted(names, key=lambda n: (n[:4] not in ALWAYS, n))]


METHODS = pick("m")


def score_run(item):
    rid, ms = item
    row = {"run": rid, "calls": sum(r == "assistant" for r, _ in ms)}
    for m in METHODS:
        row[m.__name__] = core.replay(ms, m.policy)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local")
    ap.add_argument("--jsonl")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--out", default="results")
    ap.add_argument("--label", default="")
    ap.add_argument("--group", default="m", help="method file prefixes to run, e.g. 'bc'")
    ap.add_argument("--test-half", action="store_true", help="score only runs the predictor did not train on")
    a = ap.parse_args()
    global METHODS
    METHODS = pick(a.group)
    runs = core.load_local(a.local) if a.local else core.load_jsonl(a.jsonl, a.limit)
    if a.test_half:
        from .predict import is_train
        runs = [r for r in runs if not is_train(r[0])]
    with Pool() as p:
        rows = p.map(score_run, runs, chunksize=8)
    os.makedirs(a.out, exist_ok=True)

    base_key = "lab.methods.m00_baseline"
    B = sum(r[base_key][0] for r in rows)
    from collections import Counter
    share = Counter()
    for _, ms in runs:
        for t, (role, _) in enumerate(ms):
            if role == "assistant":
                for r, c in ms[:t]:
                    share[r] += core.toks(c)
    S = sum(share.values()) or 1
    mix = " · ".join(f"{k} {v / S:.0%}" for k, v in share.most_common())
    lines = [f"# Agent context lab — {a.label or (a.local or a.jsonl)}", "",
             f"Runs: {len(rows)} · model calls: {sum(r['calls'] for r in rows)} · "
             f"median calls per run: {statistics.median(r['calls'] for r in rows):.0f} · "
             f"baseline tokens re-read: {B:,}", "", f"What gets re-read: {mix}", "",
             "| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |",
             "|---|---|---|---|---|---|"]
    csv_rows = []
    for m in METHODS:
        k = m.__name__
        tot = sum(r[k][0] for r in rows)
        miss = sum(r[k][1] for r in rows)
        refs = sum(r[k][2] for r in rows) or 1
        per = [1 - r[k][0] / r[base_key][0] for r in rows]
        big = sum(x >= 0.30 for x in per) / len(per)
        D = sum(r[base_key][3] for r in rows) or 1
        dsave = 1 - sum(r[k][3] for r in rows) / D
        net = 1 - (sum(r[k][3] for r in rows) + sum(r[k][4] for r in rows)) / D
        lines.append(f"| {m.NAME} | {'yes' if m.LOSSLESS else 'no'} | {1 - tot / B:.1%} | {dsave:.1%} | "
                     f"{net:.1%} | {miss / refs:.1%} |")
        csv_rows.append([m.NAME, m.LOSSLESS, 1 - tot / B, dsave, net, miss / refs])
    lines += ["", "**Fixed instructions** (system prompt + task) are identical on every step; providers cache them, so the conversation column is the part a method can really change. **Net** = conversation saving after charging, for every miss, the cost of fetching the stored message back (15 tokens + its size), so nothing is lost. **Miss rate** = share of the agent's references to earlier information (names, paths, "
              "numbers, error types it wrote) that were hidden from it at that moment. 0% = it never "
              "needed something the method hid. Lossless methods can still show misses, because a pointer "
              "replaces an old copy; the agent would fetch it on request.", "",
              "## Methods", ""]
    lines += [f"- **{m.NAME}**: {m.DESCRIPTION}" for m in METHODS]
    open(os.path.join(a.out, "SUMMARY.md"), "w").write("\n".join(lines) + "\n")
    with open(os.path.join(a.out, "summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "lossless", "saved", "saved_conversation", "net_after_fetch", "miss_rate"])
        w.writerows(csv_rows)
    print("\n".join(lines[:6 + len(METHODS) + 2]))


if __name__ == "__main__":
    main()
