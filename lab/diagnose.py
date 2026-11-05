"""Where do misses come from? For one method, attribute every miss to the kind of hidden message
that held the information and how many agent steps old it was.
python -m lab.diagnose --jsonl data/swegym.jsonl --method m14_tree_echo_cap --out results/swegym"""
import argparse, importlib, os
from collections import Counter
from .core import load_jsonl, salient
from .wander import classify
from .predict import is_train


def kind(role, label):
    if role == "assistant": return "agent's own old message"
    return {"on-path view": "file view", "off-path view": "file view", "edit": "edit output",
            "search (hit)": "search result", "search (miss)": "search result",
            "run/test": "run / test output"}.get(label, "other tool output")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl"); ap.add_argument("--method"); ap.add_argument("--out"); ap.add_argument("--limit", type=int, default=3000)
    a = ap.parse_args()
    pol = importlib.import_module(f"lab.methods.{a.method}").policy
    by_kind, by_age, hidden_kind = Counter(), Counter(), Counter()
    for rid, ms in load_jsonl(a.jsonl, a.limit):
        if is_train(rid): continue
        labels, _ = classify(ms, "")
        asst = [i for i, (r, _) in enumerate(ms) if r == "assistant"]
        for t in asst:
            ctx = ms[:t]; vis = pol(ctx)
            vis_sal = set()
            for v in vis: vis_sal |= salient(v)
            lost = salient(ms[t][1]) - vis_sal
            for i, ((r, c), v) in enumerate(zip(ctx, vis)):
                if v is c: continue
                k = kind(r, labels[i]); hidden_kind[k] += 1
                hit = salient(c) & lost
                if hit:
                    by_kind[k] += len(hit); lost -= hit
                    age = sum(1 for j in asst if i < j < t)
                    by_age["1-3 steps" if age <= 3 else "4-10 steps" if age <= 10 else "11+ steps"] += 1
    T = sum(by_kind.values()) or 1
    lines = [f"# Where misses come from — {a.method}", "", "| Hidden item | Share of misses | Misses per 1,000 hidden items |", "|---|---|---|"]
    lines += [f"| {k} | {v / T:.0%} | {1000 * v / max(1, hidden_kind[k]):.0f} |" for k, v in by_kind.most_common()]
    A = sum(by_age.values()) or 1
    lines += ["", "| Age of hidden item when needed | Share |", "|---|---|"] + [f"| {k} | {v / A:.0%} |" for k, v in sorted(by_age.items())]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, f"MISSES_{a.method}.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
