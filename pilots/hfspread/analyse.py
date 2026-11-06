"""Can the first two weeks of an open model's 'family tree' predict how big it gets by day 180?

For each base model (released >= 180 days before collection): derivatives (fine-tunes, quantisations,
adapters, merges) created by day 7 and 14, distinct authors, and the mix of derivative types.
Target: log(derivatives by day 180). Grouped cross-validation by organisation (a lab's models are never
in train and test together). Score: Spearman rank correlation and top-10 hit rate.
"""
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import GroupKFold

NOW = datetime(2026, 11, 6)
P = lambda s: datetime.fromisoformat(s.replace("Z", "")[:19])
trees = json.load(open("data/hfspread/trees.json"))
rows = []
for t in trees:
    c = P(t["createdAt"])
    if c > NOW - timedelta(days=180) or not t["derivatives"]:
        continue
    ds = [(P(d), a, tags) for d, a, tags in t["derivatives"] if d]
    def upto(days):
        return [x for x in ds if x[0] <= c + timedelta(days=days)]
    w7, w14, w180 = upto(7), upto(14), upto(180)
    kinds = lambda xs, k: sum(any(k in tg for tg in x[2]) for x in xs)
    rows.append({"base": t["base"], "org": t["base"].split("/")[0], "created": c.date(),
                 "n7": len(w7), "n14": len(w14), "a7": len({x[1] for x in w7}), "a14": len({x[1] for x in w14}),
                 "q14": kinds(w14, "quantized"), "f14": kinds(w14, "finetune"), "ad14": kinds(w14, "adapter"),
                 "m14": kinds(w14, "merge"), "n180": len(w180),
                 "capped": t["capped"] and ds[-1][0] < c + timedelta(days=180)})
d = pd.DataFrame(rows)
L = np.log1p
d["y"] = L(d.n180)
X = {"day-14 count only": ["ln14"],
     "+ day-7 count (speed)": ["ln14", "ln7"],
     "+ distinct authors (breadth)": ["ln14", "ln7", "la14", "la7"],
     "+ type mix (quant / fine-tune / adapter / merge)": ["ln14", "ln7", "la14", "la7", "sq", "sf", "sa", "sm"]}
d["ln14"], d["ln7"], d["la14"], d["la7"] = L(d.n14), L(d.n7), L(d.a14), L(d.a7)
for k, c in (("sq", "q14"), ("sf", "f14"), ("sa", "ad14"), ("sm", "m14")):
    d[k] = d[c] / d.n14.clip(lower=1)
d["authors_per_deriv"] = d.a14 / d.n14.clip(lower=1)

g = d.org.values
k = min(5, d.org.nunique())
out = ["# Open-model family trees: does week 1–2 predict day 180?", "",
       f"Base models: {len(d)} from {d.org.nunique()} organisations, released {d.created.min()} – {d.created.max()}. "
       f"Median derivatives by day 180: {int(d.n180.median()):,} (max {d.n180.max():,}; {int(d.capped.sum())} hit the "
       "20k download cap, counted as 20k). Cross-validation grouped by organisation.", "",
       "| Predictors | Rank correlation with day-180 size | Top-10 caught | Typical error (×) |", "|---|---|---|---|"]
top = set(d.nlargest(10, "n180").index)
for name, f in X.items():
    p = np.zeros(len(d))
    for tr, te in GroupKFold(k).split(d, groups=g):
        m = RidgeCV(alphas=np.logspace(-3, 3, 13)).fit(d.iloc[tr][f], d.iloc[tr].y)
        p[te] = m.predict(d.iloc[te][f])
    rho = spearmanr(p, d.y).statistic
    hit = len(top & set(d.index[np.argsort(-p)[:10]]))
    err = np.exp(np.median(np.abs(p - d.y)))
    out.append(f"| {name} | {rho:.2f} | {hit}/10 | {err:.2f}× |")
# which early signal matters: among models with similar day-14 counts, do more distinct authors mean bigger trees?
d["resid"] = d.y - np.poly1d(np.polyfit(d.ln14, d.y, 1))(d.ln14)
r = spearmanr(d.authors_per_deriv, d.resid).statistic
out += ["", f"Holding the day-14 count fixed, breadth (authors per derivative) vs later growth: rank correlation {r:+.2f}.",
        "", "## Biggest trees", "", "| Base model | Released | Day 14 | Authors day 14 | Day 180 |", "|---|---|---|---|---|"]
for _, x in d.nlargest(12, "n180").iterrows():
    out.append(f"| {x.base} | {x.created} | {x.n14:,} | {x.a14:,} | {x.n180:,}{'+' if x.capped else ''} |")
open("results/hfspread/HFSPREAD.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
