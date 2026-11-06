"""Children's chest X-rays with very little data.

Question: if a hospital only has 10–250 labelled CHILD X-rays, does a model pretrained on ADULT chest
X-rays (torchxrayvision, trained on ~800k adult images) beat a generic image model (ImageNet ResNet50)?
Data: Kermany et al. 2018 paediatric chest X-ray set (ages 1–5, Guangzhou), pneumonia vs normal,
official test split (624 images).
For each N per class we train a logistic regression on frozen features, 20 random draws, and report
test AUC. Also the adult model's own 'Pneumonia' score with zero child training (zero-shot).
Usage: python kids.py <folder containing train/ and test/ with NORMAL and PNEUMONIA>
"""
import glob
import os
import sys

import numpy as np
import torch
import torchvision
import torchxrayvision as xrv
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

ROOT = sys.argv[1]
torch.set_num_threads(os.cpu_count())


def files(split):
    out = []
    for lab, y in (("NORMAL", 0), ("PNEUMONIA", 1)):
        out += [(f, y) for f in sorted(glob.glob(f"{ROOT}/**/{split}/{lab}/*.jpeg", recursive=True))]
    return out


tr, te = files("train"), files("test")
print("train", len(tr), "test", len(te), flush=True)
adult = xrv.models.DenseNet(weights="densenet121-res224-all").eval()
inet = torchvision.models.resnet50(weights="IMAGENET1K_V2").eval()
inet.fc = torch.nn.Identity()
norm = torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
PN = adult.pathologies.index("Pneumonia")


def embed(items):
    A, I, Z = [], [], []
    with torch.no_grad():
        for k in range(0, len(items), 32):
            xa, xi = [], []
            for f, _ in items[k:k + 32]:
                im = Image.open(f).convert("L").resize((224, 224))
                g = np.asarray(im, dtype=np.float32)
                xa.append(xrv.datasets.normalize(g, 255)[None])
                xi.append(norm(torch.tensor(g / 255).repeat(3, 1, 1)))
            xa = torch.tensor(np.stack(xa)); xi = torch.stack(xi).float()
            fa = adult.features2(xa)
            A.append(fa.numpy()); Z.append(torch.sigmoid(adult.classifier(fa))[:, PN].numpy())
            I.append(inet(xi).numpy())
            if k % 640 == 0:
                print(k, flush=True)
    return np.vstack(A), np.vstack(I), np.concatenate(Z)


Atr, Itr, _ = embed(tr); Ate, Ite, Zte = embed(te)
ytr = np.array([y for _, y in tr]); yte = np.array([y for _, y in te])
rng = np.random.default_rng(0)
out = ["# Children's chest X-rays with little data (pneumonia vs normal)", "",
       f"Train pool {len(tr):,} child X-rays, test {len(te)} (official split). Test AUC, mean of 20 random draws "
       "(range in brackets). 0.5 = coin flip, 1.0 = perfect.", "",
       f"Adult model, zero child images (its own 'Pneumonia' output): **{roc_auc_score(yte, Zte):.3f}**", "",
       "| Child X-rays used per class | Generic image model (ImageNet) | Adult chest X-ray model | Gain |", "|---|---|---|---|"]
for n in (5, 10, 25, 50, 100, 250, None):
    ra, ri = [], []
    for s in range(20 if n else 1):
        if n:
            idx = np.concatenate([rng.choice(np.where(ytr == c)[0], n, replace=False) for c in (0, 1)])
        else:
            idx = np.arange(len(ytr))
        for X, Xt, r in ((Atr, Ate, ra), (Itr, Ite, ri)):
            m = LogisticRegression(C=0.1, max_iter=3000, class_weight="balanced").fit(X[idx], ytr[idx])
            r.append(roc_auc_score(yte, m.predict_proba(Xt)[:, 1]))
    f = lambda r: f"{np.mean(r):.3f}" + (f" ({min(r):.2f}–{max(r):.2f})" if len(r) > 1 else "")
    out.append(f"| {n or 'all (' + str(len(tr)) + ')'} | {f(ri)} | {f(ra)} | {np.mean(ra) - np.mean(ri):+.3f} |")
os.makedirs("results/imaging", exist_ok=True)
open("results/imaging/KIDS.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
