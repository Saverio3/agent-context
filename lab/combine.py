"""Merge per-group results into results/<dataset>/ALL.md, sorted by net saving, with the
efficient frontier marked (no other method saves more AND misses less)."""
import csv, glob, os, sys


def main(root):
    for ds in sorted(os.listdir(root)):
        rows = {}
        for f in glob.glob(os.path.join(root, ds, "*", "summary.csv")):
            for r in csv.DictReader(open(f)):
                rows[r["method"]] = (float(r["saved_conversation"]), float(r["net_after_fetch"]), float(r["miss_rate"]))
        if not rows:
            continue
        items = sorted(rows.items(), key=lambda kv: -kv[1][1])
        real = [(m, v) for m, v in items if not m.startswith("CEILING")]
        front = {m for m, (_, n, mi) in real
                 if not any(n2 > n and mi2 <= mi for m2, (_, n2, mi2) in real if m2 != m)}
        lines = [f"# {ds}: all methods, sorted by net saving (★ = best trade-off: nothing saves more at equal or lower risk)", "",
                 "| | Method | Saved (conversation) | Net after fetch-back | Miss rate |", "|---|---|---|---|---|"]
        lines += [f"| {'★' if m in front else ''} | {m} | {s:.1%} | {n:.1%} | {mi:.1%} |" for m, (s, n, mi) in items]
        open(os.path.join(root, ds, "ALL.md"), "w").write("\n".join(lines) + "\n")
        print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results")
