"""Piece B: how to catch a CAREFUL AI agent with far fewer decoys and far fewer days.

Same budget for every defender strategy: 1,000 decoys/lures. Goal: 5 sightings (enough to name it, ~99%).
Careful agents (all spend similar effort):
  random scanner     1,000 probes/hour spread over all 3.7 billion IPv4 addresses (the old-worm model)
  habitat forager    same effort, but like an animal foraging it spends 90% of probes where food is likely:
                     cloud / GPU-hosting ranges (assumed 2% of the address space)
  searcher           finds targets the way an AI does: 20 target-hunting searches per day, looks at 10 results,
                     picks 3 (pick rates for lures measured in the lure pilot when available)
  searcher + trails  as searcher, and like an ant following a scent trail it follows leads found on a target
                     (credentials, links) with probability 0.6 per hop, up to 5 hops
Defender strategies (all 1,000 items):
  scatter            decoys at random addresses (what passive sensor networks resemble)
  habitat decoys     decoys placed inside cloud / GPU-hosting ranges
  search lures       lures where AI looks (search results, code sites); a search shows one with prob f = 20%
  lures + trails     lures that contain fake credentials/links pointing to other decoys (chains of 5)
  + tailored         after the first sightings the agent is fingerprinted (correct 75% of the time) and
                     lures matched to that model's preferences replace generic ones
  portfolio          500 habitat decoys + 500 lures with trails + tailoring (robust mix)
Output: median days to 5 sightings (capped at 3 years) over 400 simulated agents. Assumptions are explicit;
the lure pick-rates come from the measured pilot if results/lures/*.json exist.
"""
import glob
import json

import numpy as np

SPACE, HAB_SHARE = 3.7e9, 0.02
PROBES_H = 1000.0
SEARCH_D, F_LURE = 20.0, 0.20
CAP = 3 * 365 * 24
rng = np.random.default_rng(5)

# lure pick rates: average lure vs best lure for a given model (from the lure pilot if available)
p_avg, p_best, p_ord = 0.40, 0.60, 0.25
files = [f for f in glob.glob("results/lures/*.json") if "recon_" not in f]
if files:
    av, be, od = [], [], []
    for f in files:
        pr = json.load(open(f))["pick_rate"]
        lures = [v[0] for k, v in pr.items() if k != "ordinary result" and v[0] is not None]
        if lures:
            av.append(np.mean(lures)); be.append(max(lures)); od.append(pr["ordinary result"][0])
    if av:
        p_avg, p_best, p_ord = float(np.mean(av)), float(np.mean(be)), float(np.mean(od))


def days_to_5(agent, strat, n=400):
    hab = {"habitat decoys": 1000, "portfolio": 500}.get(strat, 0)
    scat = 1000 if strat == "scatter" else 0
    lures = {"search lures": 1000, "lures + trails": 1000, "+ tailored": 1000, "portfolio": 500}.get(strat, 0)
    trails = strat in ("lures + trails", "+ tailored", "portfolio")
    tailored = strat in ("+ tailored", "portfolio")
    out = []
    for _ in range(n):
        seen, t, ident = 0, 0, False
        while seen < 5 and t < CAP:
            t += 1
            # address-space probing
            if agent in ("random scanner", "habitat forager"):
                hab_frac = 0.9 if agent == "habitat forager" else HAB_SHARE
                r_hab = PROBES_H * hab_frac * hab / (SPACE * HAB_SHARE)
                r_scat = PROBES_H * scat / SPACE
                seen += rng.poisson(r_hab + r_scat)
            else:
                # searching: each search shows a lure with prob f (scaled by how many lures we placed)
                f = F_LURE * lures / 1000
                p = p_best if (tailored and ident) else p_avg
                hits = rng.poisson(SEARCH_D / 24 * f * p)
                for _ in range(hits):
                    seen += 1
                    if trails and agent == "searcher + trails":
                        for _ in range(5):
                            if rng.random() < 0.6:
                                seen += 1
                            else:
                                break
                if tailored and not ident and seen >= 2:
                    ident = rng.random() < 0.75
        out.append(min(t, CAP) / 24)
    return float(np.median(out))


AG = ["random scanner", "habitat forager", "searcher", "searcher + trails"]
ST = ["scatter", "habitat decoys", "search lures", "lures + trails", "+ tailored", "portfolio"]
L = ["# Catching a careful AI agent: strategies compared (same 1,000-item budget)", "",
     f"Median days until 5 sightings over 400 simulated agents (capped at 1,095 days = 3 years). Lure pick rates used: "
     f"average lure {p_avg:.0%}, best lure for that model {p_best:.0%}, ordinary result {p_ord:.0%}"
     f"{' (measured in the lure pilot)' if files else ' (placeholders: lure pilot not finished)'}. "
     "Effort: 1,000 probes/hour or 20 target searches/day.", "",
     "| Defender strategy | " + " | ".join(AG) + " |", "|---|" + "---|" * len(AG)]
for s in ST:
    cells = []
    for a in AG:
        d = days_to_5(a, s)
        cells.append("never (3y+)" if d >= 1095 else (f"{d * 24:.0f} h" if d < 2 else f"{d:.0f} days"))
    L.append(f"| {s} | " + " | ".join(cells) + " |")
L += ["", "Reference from the earlier decoy maths: random-scan decoys need 100,000 to see a 1,000-probes/hour agent 5 "
      "times in ~8 days.", "",
      "Key assumptions: cloud/GPU ranges = 2% of address space; foragers put 90% of probes there; 20 target searches/day; "
      "1,000 lures make a lure appear in 20% of relevant searches; trails followed with prob 0.6 per hop."]
open("results/huntsim/HUNTSIM.md", "w").write("\n".join(L) + "\n") if __import__("os").makedirs("results/huntsim", exist_ok=True) is None else None
print("\n".join(L))
