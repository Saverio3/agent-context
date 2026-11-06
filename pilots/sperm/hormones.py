"""Pilot: can a semen VIDEO hint at hormone problems? (VISEM, 85 men)

For each man's video: motion statistics from dense optical flow (no sperm detector needed):
how much of the field moves, how fast (percentiles), how coherent the directions are, how
bursty over time. Targets: serum testosterone, FSH, LH, inhibin B, SHBG, oestradiol,
seminal & serum AMH; plus progressive motility as a sanity check.
Leave-one-man-out ridge prediction + permutation test (2,000 shuffles) of the best single feature,
Bonferroni-adjusted for the number of features tried.
Usage: python hormones.py <dir with videos/*.avi and csvs>   (fetch_visem.py downloads them)
"""
import glob
import os
import re
import sys

import cv2
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV

ROOT = sys.argv[1]
SECONDS, STEP = 60, 2  # analyse first 60 s, every 2nd frame
rng = np.random.default_rng(0)


def video_features(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 50
    prev, mags, movers, coh, energy = None, [], [], [], []
    n = 0
    while n < SECONDS * fps:
        ok, fr = cap.read()
        if not ok:
            break
        n += 1
        if n % STEP:
            continue
        g = cv2.cvtColor(cv2.resize(fr, (320, 240)), cv2.COLOR_BGR2GRAY)
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 2, 9, 2, 5, 1.1, 0)
            m = np.hypot(fl[..., 0], fl[..., 1]) * fps / STEP  # px/s at 320 wide
            mv = m > 5
            mags.append(np.percentile(m[mv], [50, 90, 99]) if mv.sum() > 20 else [0, 0, 0])
            movers.append(mv.mean())
            if mv.sum() > 20:
                ang = np.arctan2(fl[..., 1][mv], fl[..., 0][mv])
                coh.append(np.abs(np.exp(1j * ang).mean()))
            energy.append(m.mean())
        prev = g
    cap.release()
    if len(energy) < 20:
        return None
    M = np.array(mags); e = np.array(energy)
    return {"moving share": np.mean(movers), "speed p50": M[:, 0].mean(), "speed p90": M[:, 1].mean(),
            "speed p99": M[:, 2].mean(), "direction coherence": np.mean(coh) if coh else 0,
            "motion energy": e.mean(), "burstiness": e.std() / max(e.mean(), 1e-9),
            "energy trend": np.polyfit(np.arange(len(e)), e, 1)[0] / max(e.mean(), 1e-9)}


rows = []
PRE = os.environ.get("FEATURES")
for v in ([] if PRE else sorted([p for p in glob.glob(f"{ROOT}/**/*", recursive=True) if p.lower().endswith((".avi", ".mp4"))])):
    m = re.search(r"(\d+)", os.path.basename(v))
    f = video_features(v)
    if f and m:
        f["ID"] = int(m.group(1)); f["file"] = os.path.basename(v); rows.append(f)
        print(os.path.basename(v), "ok", flush=True)
F = pd.read_csv(PRE) if PRE else pd.DataFrame(rows)
if "file" not in F: F["file"] = F.ID.astype(str) + ".avi"
vm = [x for x in glob.glob(f"{ROOT}/**/*videos*.csv", recursive=True)]
if vm:  # official video -> participant mapping, if present
    t = pd.read_csv(vm[0], sep=";" if ";" in open(vm[0], encoding="utf-8-sig").readline() else ",", encoding="utf-8-sig"); print(t.head())
    fc = next((c for c in t.columns if t[c].astype(str).str.contains(r"\.avi|\.mp4", case=False).any()), None)
    if fc is not None:
        mp = {os.path.splitext(os.path.basename(str(a)))[0]: b for a, b in zip(t[fc], t[t.columns[0]])}
        F["ID"] = [int(mp.get(os.path.splitext(x)[0], i)) for x, i in zip(F.file, F.ID)]
F = F.drop(columns="file")
os.makedirs("results/sperm", exist_ok=True)
F.to_csv("results/sperm/video_features_raw.csv", index=False)  # save before anything can fail
F = F.groupby("ID").mean().reset_index()


def load(name):
    p = [x for x in glob.glob(f"{ROOT}/**/*{name}*.csv", recursive=True) if "Train" not in os.path.basename(x)] or \
        glob.glob(f"{ROOT}/**/*{name}*.csv", recursive=True)
    if not p:
        return None
    head = open(p[0], encoding="utf-8-sig").readline()
    d = pd.read_csv(p[0], sep=";" if head.count(";") > head.count(",") else ",", encoding="utf-8-sig")
    d.columns = [c.strip() for c in d.columns]
    print(name, p[0], d.shape, list(d.columns)[:6]); print(d.head(3))
    d = d.rename(columns={d.columns[0]: "ID"})
    return d.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "."), errors="coerce"))


hor = load("sex_hormones"); sem = load("semen_analysis")
df = F.merge(hor, on="ID", how="inner")
if sem is not None:
    keep = [c for c in sem.columns if c == "ID" or "Progressive" in c]
    df = df.merge(sem[keep], on="ID", how="left")
X = [c for c in F.columns if c != "ID"]
targets = [c for c in df.columns if c not in X and c != "ID"]


def perm_p(x, y, n=2000):
    r0 = abs(spearmanr(x, y).statistic)
    return (1 + sum(abs(spearmanr(x, rng.permutation(y)).statistic) >= r0 for _ in range(n))) / (n + 1)


out = ["# Semen video → hormones (VISEM)", "",
       f"Men with video + hormones: {len(df)}. Video features: {', '.join(X)}. "
       "Leave-one-man-out ridge; p from 2,000 shuffles, adjusted for trying every feature.", "",
       "| Blood/semen value | Men | Best video feature | Rank corr. | p (adjusted) | Leave-one-out prediction vs truth |",
       "|---|---|---|---|---|---|"]
for t in targets:
    d = df.dropna(subset=[t] + X)
    if len(d) < 20:
        continue
    cs = {x: spearmanr(d[x], d[t]).statistic for x in X}
    best = max(cs, key=lambda k: abs(np.nan_to_num(cs[k])))
    p = perm_p(d[best].values, d[t].values)
    Z = (d[X] - d[X].mean()) / d[X].std().replace(0, 1)
    y = np.log1p(d[t].clip(lower=0).values)
    pred = np.zeros(len(d))
    for i in range(len(d)):
        msk = np.arange(len(d)) != i
        pred[i] = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(Z[msk], y[msk]).predict(Z.iloc[[i]])[0]
    loo = spearmanr(pred, y).statistic
    out.append(f"| {t} | {len(d)} | {best} | {cs[best]:+.2f} | {p:.3f} ({min(1, p * len(X)):.2f}) | {loo:+.2f} |")
os.makedirs("results/sperm", exist_ok=True)
open("results/sperm/HORMONES.md", "w").write("\n".join(out) + "\n")
F.to_csv("results/sperm/video_features.csv", index=False)
print("\n".join(out))
