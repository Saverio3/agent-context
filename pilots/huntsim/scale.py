"""Does a bigger budget (100 -> 100,000 decoys/lures) buy speed? Same agents and assumptions as huntsim.py,
with diminishing returns for lures: the share of an agent's target searches that show one of our lures is
1 - exp(-lures / 4,481) (so 1,000 lures -> 20%, 10,000 -> 89%). Habitat decoys scale linearly (more decoys in
cloud/GPU ranges = proportionally more hits). Measured lure pick rates from the lure pilot."""
import glob
import json
import math
import os

import numpy as np

rng = np.random.default_rng(9)
files = [f for f in glob.glob("results/lures/*.json") if "recon_" not in f]
av, be = [], []
for f in files:
    pr = json.load(open(f))["pick_rate"]
    l = [v[0] for k, v in pr.items() if k != "ordinary result" and v[0] is not None]
    av.append(np.mean(l)); be.append(max(l))
p_avg, p_best = float(np.mean(av)), float(np.mean(be))
SPACE, HAB = 3.7e9, 0.02
CAP = 3 * 365 * 24


def sim(agent, budget, n=300):
    out = []
    for _ in range(n):
        seen, t, ident = 0, 0, False
        while seen < 5 and t < CAP:
            t += 1
            if agent == "forager":
                seen += rng.poisson(1000 * 0.9 * budget / (SPACE * HAB))
            elif agent == "random scanner":
                seen += rng.poisson(1000 * budget / SPACE)
            else:
                f = 1 - math.exp(-budget / 4481)
                hits = rng.poisson(20 / 24 * f * (p_best if ident else p_avg))
                for _ in range(hits):
                    seen += 1
                    if agent == "searcher + trails":
                        for _ in range(5):
                            if rng.random() < 0.6:
                                seen += 1
                            else:
                                break
                if not ident and seen >= 2:
                    ident = rng.random() < 0.75
        out.append(min(t, CAP))
    return float(np.median(out))


fmt = lambda h: "never (3y+)" if h >= CAP else (f"{h:.0f} h" if h < 48 else f"{h / 24:.0f} days")
B = [100, 1_000, 10_000, 100_000]
L = ["# More decoys = faster? (best strategy per agent type)", "",
     f"Median time to 5 sightings. Lures: tailored + trails for searchers; habitat decoys for foragers; random decoys for "
     f"random scanners. Pick rates {p_avg:.0%} avg / {p_best:.0%} tailored (measured).", "",
     "| Budget | Random internet scanner | Forager (cloud/GPU ranges) | Searcher | Searcher + trails |", "|---|---|---|---|---|"]
for b in B:
    L.append(f"| {b:,} | " + " | ".join(fmt(sim(a, b)) for a in ["random scanner", "forager", "searcher", "searcher + trails"]) + " |")
os.makedirs("results/huntsim", exist_ok=True)
open("results/huntsim/SCALE.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
