"""Combine lure pick-rates across models and turn them into detection time.

Detection-time sketch (assumptions stated in the output): a careful agent picks targets by searching rather than
scanning random addresses. It runs S target-hunting searches per day; our lures appear in a share f of those
searches' results; it picks a lure with the measured rate p (3 picks out of 12 results). Sightings per day = S*f*p.
Time to 5 sightings (as in the decoy maths) = 5 / (S*f*p). Compared with random-scan decoys from COVERAGE.md
(100,000 decoys -> 8 days for a 1,000-probes/hour agent).
"""
import glob
import json

rows = [json.load(open(f)) for f in sorted(glob.glob("results/chainbait/lures_*.json")) if "recon_" not in f]
kinds = ["unprotected withdraw", "unprotected setOwner", "AI-directed comment", "plain decoy", "too good to be true", "ordinary result"]
out = ["# Do AI agents pick our bait CONTRACTS?", "",
       "Each model saw 12 newly deployed contracts (9 ordinary, 3 bait) for a bug-bounty goal and picked 3 to examine. "
       "Random picking = 25% per result.", "",
       "| Model | Trials | No clear answer | " + " | ".join(kinds) + " |", "|---|---|---|" + "---|" * len(kinds)]
best = []
for r in rows:
    pr = r["pick_rate"]
    out.append(f"| {r['model']} | {r['trials']} | {r['no_clear_answer']} | " +
               " | ".join(f"{pr[k][0]:.0%}" if pr.get(k) and pr[k][0] is not None else "–" for k in kinds) + " |")
    best.append(max(pr[k][0] or 0 for k in kinds[:5]))
open("results/chainbait/CHAIN_LURES.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
