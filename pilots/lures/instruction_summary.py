import glob, json
rows=[json.load(open(f)) for f in sorted(glob.glob("results/instruction/*.json"))]
L=["# Does an embedded instruction help or hurt a lure?","",
   "Same attractive target shown bare vs with an instruction to the agent. Share picked among 12 results (random=25%).","",
   "| Model | Bare target | Instructed target | Ordinary result | Instruction effect |","|---|---|---|---|---|"]
for r in rows:
    pr=r["pick_rate"]; b=pr["bare"][0]; ins=pr["instructed"][0]; o=pr["ordinary"][0]
    eff = f"{(ins-b)*100:+.0f} pts" if (b is not None and ins is not None) else "-"
    L.append(f"| {r['model']} | {b:.0%} | {ins:.0%} | {o:.0%} | {eff} |")
open("results/instruction/INSTRUCTION.md","w").write("\n".join(L)+"\n"); print("\n".join(L))
