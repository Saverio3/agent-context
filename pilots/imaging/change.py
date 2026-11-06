"""'What changed since your last scan?' — NIH ChestX-ray14 repeat scans.

Question: to spot a NEW finding on today's X-ray, does it help to compare against the same patient's
previous X-ray, versus reading today's scan alone?
Data: NIH ChestX-ray14 (labels shipped inside torchxrayvision), image batches downloaded from NIH Box.
Pairs: consecutive scans of the same patient (follow-up k-1 -> k). Target: today's scan has a finding
the previous one did not (labels are text-mined from reports, so noisy).
Features from the adult torchxrayvision model (frozen):
  A  today's scan alone (18 disease scores + 1024 image features)
  B  A + the previous scan's features + the difference
Logistic regression, split by PATIENT (5-fold), AUC.
Usage: python change.py <folder with extracted images/*.png>
"""
import glob
import os
import sys

import numpy as np
import pandas as pd
import torch
import torchxrayvision as xrv
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

torch.set_num_threads(os.cpu_count())
have = {os.path.basename(f): f for f in glob.glob(f"{sys.argv[1]}/**/*.png", recursive=True)}
csv = glob.glob(os.path.join(os.path.dirname(xrv.__file__), "data", "Data_Entry_2017*.csv*"))[0]
d = pd.read_csv(csv)
d = d[d["Image Index"].isin(have)].sort_values(["Patient ID", "Follow-up #"])
d["set"] = d["Finding Labels"].apply(lambda s: frozenset() if s == "No Finding" else frozenset(s.split("|")))
pairs = []
for pid, g in d.groupby("Patient ID"):
    r = g.to_dict("records")
    for a, b in zip(r, r[1:]):
        pairs.append((pid, a["Image Index"], b["Image Index"], int(bool(b["set"] - a["set"])),
                      ", ".join(sorted(b["set"] - a["set"]))))
P = pd.DataFrame(pairs, columns=["pid", "prev", "cur", "new", "what"])
print("images", len(d), "patients", d["Patient ID"].nunique(), "pairs", len(P), "new-finding rate", P.new.mean(), flush=True)
model = xrv.models.DenseNet(weights="densenet121-res224-all").eval()
need = sorted(set(P.prev) | set(P.cur))
emb = {}
with torch.no_grad():
    for k in range(0, len(need), 32):
        xs = []
        for n in need[k:k + 32]:
            g = np.asarray(Image.open(have[n]).convert("L").resize((224, 224)), dtype=np.float32)
            xs.append(xrv.datasets.normalize(g, 255)[None])
        x = torch.tensor(np.stack(xs))
        f = model.features2(x)
        s = torch.sigmoid(model.classifier(f))
        for n, a, b in zip(need[k:k + 32], f.numpy(), s.numpy()):
            emb[n] = np.concatenate([b, a])
        if k % 1600 == 0:
            print(k, flush=True)
cur = np.stack([emb[n] for n in P.cur]); prev = np.stack([emb[n] for n in P.prev])
X = {"Today's scan alone": cur, "Today + previous scan + difference": np.hstack([cur, prev, cur - prev]),
     "Difference only": cur - prev}
y = P.new.values
out = ["# What changed since your last scan? (NIH ChestX-ray14 repeat scans)", "",
       f"{len(d):,} X-rays from {d['Patient ID'].nunique():,} patients → {len(P):,} consecutive pairs; "
       f"{y.mean():.0%} of pairs show a finding the previous scan didn't have. 5-fold split by patient. "
       "Labels are text-mined from reports (noisy), so absolute AUCs are capped.", "",
       "| What the model sees | AUC for 'new finding today' |", "|---|---|"]
for name, M in X.items():
    p = np.zeros(len(y))
    for a, b in GroupKFold(5).split(M, y, P.pid):
        mu, sd = M[a].mean(0), M[a].std(0) + 1e-6
        m = LogisticRegression(C=0.05, max_iter=3000).fit((M[a] - mu) / sd, y[a])
        p[b] = m.predict_proba((M[b] - mu) / sd)[:, 1]
    out.append(f"| {name} | {roc_auc_score(y, p):.3f} |")
top = P[P.new == 1].what.str.split(", ").explode().value_counts().head(6)
out += ["", "Most common new findings: " + ", ".join(f"{k} ({v})" for k, v in top.items())]
os.makedirs("results/imaging", exist_ok=True)
open("results/imaging/CHANGE.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
