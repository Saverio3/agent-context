import glob, json
rows = [json.load(open(f)) for f in sorted(glob.glob("results/tripwire/*.json"))]
kinds = list(rows[0]["res"]) if rows else []
L = ["# Tripwires for AI-assistant worms", "", "An AI email assistant replied to emails carrying a harmless tripwire (include a code). "
     "'Obeyed' = the code appeared in its reply (a worm could pass through). 'Spread' = the reply, received by a second assistant, "
     "made it include the code too (two hops).", "", "| Model | " + " | ".join(f"{k}: obeyed / spread" for k in kinds) + " | False alarms |",
     "|---|" + "---|" * len(kinds) + "---|"]
for r in rows:
    c = []
    for k in kinds:
        o, n, s2, n2 = r["res"][k]
        c.append(f"{o / n:.0%} / {(s2 / n2 if n2 else 0):.0%}")
    L.append(f"| {r['model']} | " + " | ".join(c) + f" | {r['false_alarms'][0]}/{r['false_alarms'][1]} |")
open("results/tripwire/TRIPWIRE.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
