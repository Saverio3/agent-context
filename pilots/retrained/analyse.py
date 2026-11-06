"""Does the fingerprint survive hacker modification? Train on ORIGINAL models' commands (half the tasks),
test on held-out tasks for (a) the originals, (b) the modified ('abliterated', safety-removed) versions.
Also compares bait pick-rates original vs modified."""
import glob, json, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
rows = sum([json.load(open(f)) for f in glob.glob("results/retrained/cmds_*.json")], [])
orig = [r for r in rows if "abl" not in r["label"]]; mod = [r for r in rows if "abl" in r["label"]]
tr = [r for r in orig if r["task"] % 2 == 0]; te_o = [r for r in orig if r["task"] % 2 == 1]; te_m = [r for r in mod if r["task"] % 2 == 1]
v = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)
X = v.fit_transform([r["text"] for r in tr]); clf = LogisticRegression(max_iter=3000, C=4).fit(X, [r["family"] for r in tr])
acc = lambda s: np.mean(clf.predict(v.transform([r["text"] for r in s])) == np.array([r["family"] for r in s])) if s else float("nan")
fams = sorted({r["family"] for r in orig})
L = ["# Does the fingerprint survive hacker modification?", "",
     f"Commands for 30 everyday admin tasks (x2). Trained on original models ({', '.join(fams)}) using half the tasks; tested on the other half. "
     f"Random = {1/len(fams):.0%}.", "", "| Tested on | Answers | Named the right family |", "|---|---|---|",
     f"| Original models (unseen tasks) | {len(te_o)} | {acc(te_o):.0%} |"]
for lab in sorted({r['label'] for r in mod}):
    s = [r for r in te_m if r["label"] == lab]
    L.append(f"| {lab} (safety removed) | {len(s)} | {acc(s):.0%} |")
L += ["", "## Bait: original vs safety-removed", "", "| Model | Ordinary result | Best lure | Average lure |", "|---|---|---|---|"]
for f in sorted(glob.glob("results/retrained/lures_*.json")):
    d = json.load(open(f)); pr = d["pick_rate"]; lr = [v[0] for k, v in pr.items() if k != "ordinary result" and v[0] is not None]
    L.append(f"| {d['model']} | {pr['ordinary result'][0]:.0%} | {max(lr):.0%} | {np.mean(lr):.0%} |")
open("results/retrained/RETRAINED.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
