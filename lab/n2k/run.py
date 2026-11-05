"""python -m lab.n2k.run data/chatdev  -> results/need_to_know/SUMMARY.md"""
import glob, os, sys, statistics
from .parse import parse
from .methods import ALL


def main(folder, out="results/need_to_know"):
    runs = [parse(p)[0] for p in sorted(glob.glob(os.path.join(folder, "*.log")))]
    runs = [r for r in runs if len(r) >= 6]
    res = {m.name: [m.run(r) for r in runs] for m in ALL}
    base = res[ALL[0].name]
    B = sum(x[0] for x in base)
    lines = [f"# Need-to-know lab — {len(runs)} ChatDev multi-agent runs, "
             f"{sum(len(r) for r in runs)} messages, {B:,} tokens sent today", "",
             "| Method | Tokens sent | Saved vs plain | Median per run | Miss rate |", "|---|---|---|---|---|"]
    for m in ALL:
        rs = res[m.name]
        T = sum(x[0] for x in rs); mi = sum(x[1] for x in rs); rf = sum(x[2] for x in rs) or 1
        per = [1 - x[0] / b[0] for x, b in zip(rs, base)]
        lines.append(f"| {m.name} | {T:,} | {1 - T / B:.1%} | {statistics.median(per):.1%} | {mi / rf:.1%} |")
    lines += ["", "Tokens ≈ characters/4. Role system prompts are excluded (they are cacheable instructions, "
              "not messages). Pull methods assume the receiver asks for what its next reply mentions; "
              "requests cost 15 tokens each. Miss rate = receiver references to earlier content it could not see.",
              "", "## Methods", ""] + [f"- **{m.name}**: {m.desc}" for m in ALL]
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "SUMMARY.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:5 + len(ALL)]))


if __name__ == "__main__":
    main(sys.argv[1])
