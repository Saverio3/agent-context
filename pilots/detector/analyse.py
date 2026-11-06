"""Leave-one-workload-out test: train on all other workloads, test on the unseen one.
For an AI workload: share of its windows flagged (detection). For an ordinary one: share flagged (false alarm)."""
import csv, os, sys
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier


def evaluate(path, title):
    rows = list(csv.DictReader(open(path)))
    feats = [k for k in rows[0] if k not in ("kind", "label", "rep")]
    X = np.array([[float(r[k]) for k in feats] for r in rows]); y = np.array([int(r["kind"]) for r in rows])
    labels = [r["label"] for r in rows]
    if len(set(y)) < 2:
        return [f"### {title}", "", "Not tested: no AI windows were captured in this run.", ""]
    out = [f"### {title}", "", "| Workload (never seen in training) | AI? | Windows | Flagged as AI |", "|---|---|---|---|"]
    det, fa = [], []
    for lab in sorted(set(labels), key=lambda l: (-int(next(r['kind'] for r in rows if r['label'] == l)), l)):
        te = np.array([l == lab for l in labels])
        if len(set(y[~te])) < 2:  # the only AI workload: hold out one repetition at a time instead
            reps = np.array([r["rep"] for r in rows]); ps = []
            for rp in sorted(set(reps[te])):
                t2 = te & (reps == rp)
                ps.append(GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=0).fit(X[~t2], y[~t2]).predict(X[t2]))
            p = np.concatenate(ps).mean(); lab = lab + " (only AI type: unseen repetition, not unseen workload)"
        else:
            clf = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=0).fit(X[~te], y[~te])
            p = clf.predict(X[te]).mean()
        is_ai = int(y[te][0])
        (det if is_ai else fa).append(p)
        out.append(f"| {lab} | {'yes' if is_ai else 'no'} | {te.sum()} | {p:.0%} |")
    clf = GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=0).fit(X, y)
    imp = sorted(zip(clf.feature_importances_, feats), reverse=True)[:5]
    out += ["", f"Average detection of unseen AI workloads: **{np.mean(det):.0%}** · average false alarm on unseen ordinary workloads: **{np.mean(fa):.0%}**",
            "", "Most telling signals: " + ", ".join(f"{f} ({v:.2f})" for v, f in imp), ""]
    return out


if __name__ == "__main__":
    lines = ["# On-device and network AI detector pilot", ""]
    if os.path.exists("data/detector/process.csv"):
        lines += evaluate("data/detector/process.csv", "A. Is an AI model running on this computer? (process signals)")
    if os.path.exists("data/detector/network.csv"):
        lines += evaluate("data/detector/network.csv", "B. Is an AI model split across devices? (network traffic only)")
    os.makedirs("results/detector", exist_ok=True)
    open("results/detector/DETECTOR.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
