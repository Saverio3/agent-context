"""Combine lure pick-rates across models and turn them into detection time.

Detection-time sketch (assumptions stated in the output): a careful agent picks targets by searching rather than
scanning random addresses. It runs S target-hunting searches per day; our lures appear in a share f of those
searches' results; it picks a lure with the measured rate p (3 picks out of 12 results). Sightings per day = S*f*p.
Time to 5 sightings (as in the decoy maths) = 5 / (S*f*p). Compared with random-scan decoys from COVERAGE.md
(100,000 decoys -> 8 days for a 1,000-probes/hour agent).
"""
import glob
import json

rows = [json.load(open(f)) for f in sorted(glob.glob("results/lures/*.json"))]
kinds = ["high-value bait", "leaked secret", "AI-directed note", "plain decoy", "too good to be true", "ordinary result"]
out = ["# Do AI agents take AI-targeted bait?", "",
       "Each model saw 12 search results (9 ordinary, 3 lures) for a security-testing goal and picked 3 to investigate. "
       "Random picking = 25% per result.", "",
       "| Model | Trials | No clear answer | " + " | ".join(kinds) + " |", "|---|---|---|" + "---|" * len(kinds)]
best = []
for r in rows:
    pr = r["pick_rate"]
    out.append(f"| {r['model']} | {r['trials']} | {r['no_clear_answer']} | " +
               " | ".join(f"{pr[k][0]:.0%}" if pr.get(k) and pr[k][0] is not None else "–" for k in kinds) + " |")
    best.append(max(pr[k][0] or 0 for k in kinds[:5]))
if best:
    p = sorted(best)[len(best) // 2]
    out += ["", f"Median best-lure pick rate across models: **{p:.0%}**.", "",
            "## What that could mean for detection time (assumption-based sketch)", "",
            "| Target-hunting searches per day (S) | Lure appears in share f of them | Days to 5 sightings |", "|---|---|---|"]
    for S in (5, 20, 100):
        for f in (0.05, 0.2, 0.5):
            out.append(f"| {S} | {f:.0%} | {5 / (S * f * p):.1f} |")
    out += ["", "Random-scan decoys for a careful agent (from the decoy maths): 100,000 decoys → ~8 days; 10,000 → ~2.5 months. "
            "The lure sketch only holds if careful agents choose targets by searching; S and f are assumptions, p is measured."]
open("results/lures/LURES.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
