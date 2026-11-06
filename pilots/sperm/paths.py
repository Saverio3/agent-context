"""Sperm 'migration map' pilot: does HOW sperm swim tell you about the sample — even DNA damage?

Data: VISEM-Tracking (Zenodo 7293726), 20 men, ~30 s video each, every sperm boxed in every frame
with a track ID; plus each man's lab semen analysis (motility, morphology, DNA fragmentation DFI).

Per track (>= 1 s long): curvilinear speed VCL, straight-line speed VSL, straightness LIN = VSL/VCL,
wobble (side-to-side distance from the smoothed path), turning sharpness. Per man: medians, spread,
and share of 'fast and straight' swimmers.
Tests (leave-one-man-out, 20 men):
  sanity  - do path features recover the lab's progressive motility? (should, if tracks are good)
  new     - do they predict DNA fragmentation (DFI) and normal morphology, which labs measure with
            separate, slower stains/tests?
Permutation test (2,000 shuffles) for each correlation, because n = 20 is tiny.
Usage: python paths.py <folder with VISEM_Tracking_Train_v4 and csvs>
"""
import glob
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV

ROOT = sys.argv[1]
FPS, W, H = 50, 640, 480
rng = np.random.default_rng(0)

feats = []
for vdir in sorted(glob.glob(f"{ROOT}/VISEM_Tracking_Train_v4/Train/*")):
    vid = int(os.path.basename(vdir))
    tracks = defaultdict(list)
    for f in glob.glob(f"{vdir}/labels_ftid/*.txt"):
        fr = int(os.path.basename(f).split("_frame_")[1].split("_")[0])
        for line in open(f):
            p = line.split()
            if len(p) >= 6 and p[1] == "0":  # class 0 = sperm
                tracks[p[0]].append((fr, float(p[2]) * W, float(p[3]) * H))
    rows = []
    for t in tracks.values():
        t.sort()
        a = np.array(t)
        if len(a) < FPS:
            continue
        fr, xy = a[:, 0], a[:, 1:]
        dur = (fr[-1] - fr[0]) / FPS
        steps = np.linalg.norm(np.diff(xy, axis=0), axis=1)
        vcl = steps.sum() / dur
        vsl = np.linalg.norm(xy[-1] - xy[0]) / dur
        k = 9
        sm = np.vstack([np.convolve(xy[:, i], np.ones(k) / k, mode="same") for i in range(2)]).T[k:-k]
        wob = np.median(np.linalg.norm(xy[k:-k] - sm, axis=1)) if len(sm) > 5 else np.nan
        d = np.diff(sm, axis=0) if len(sm) > 5 else np.zeros((2, 2))
        ang = np.arctan2(d[:, 1], d[:, 0])
        turn = np.median(np.abs(np.angle(np.exp(1j * np.diff(ang))))) if len(ang) > 2 else np.nan
        rows.append((vcl, vsl, vsl / vcl if vcl > 0 else 0, wob, turn))
    r = pd.DataFrame(rows, columns=["vcl", "vsl", "lin", "wob", "turn"])
    feats.append({"ID": vid, "tracks": len(r),
                  "speed (median)": r.vcl.median(), "straight-line speed": r.vsl.median(),
                  "straightness": r.lin.median(), "wobble": r.wob.median(), "turning": r.turn.median(),
                  "speed spread": r.vcl.quantile(.9) - r.vcl.quantile(.1),
                  "share fast & straight": ((r.vsl > 25) & (r.lin > .5)).mean(),
                  "share barely moving": (r.vcl < 10).mean()})
F = pd.DataFrame(feats)
lab = pd.read_csv(f"{ROOT}/semen_analysis_data_Train.csv")
lab.columns = [c.split(" (")[0].split(",")[0].strip() for c in lab.columns]
df = F.merge(lab, on="ID")
X = [c for c in F.columns if c not in ("ID", "tracks")]
TARGETS = {"Progressive motility": "sanity", "Immotile sperm": "sanity", "DNA fragmentation index": "new",
           "Normal spermatozoa": "new", "Sperm vitality": "new", "Sperm concentration": "new"}


def perm_p(x, y, n=2000):
    r0 = abs(spearmanr(x, y).statistic)
    return (1 + sum(abs(spearmanr(x, rng.permutation(y)).statistic) >= r0 for _ in range(n))) / (n + 1)


out = ["# Sperm paths vs lab results (VISEM-Tracking, 20 men)", "",
       f"Tracks used: {int(df.tracks.sum()):,} sperm followed for ≥1 s (median {int(df.tracks.median())} per man). "
       "Leave-one-man-out prediction; p from 2,000 label shuffles. With 20 men, only strong effects can show.", "",
       "| Lab result | Type | Best single path feature | Rank corr. | p | Leave-one-out prediction vs truth (rank corr.) |",
       "|---|---|---|---|---|---|"]
for t, kind in TARGETS.items():
    d = df.dropna(subset=[t])
    cs = {x: spearmanr(d[x], d[t]).statistic for x in X}
    best = max(cs, key=lambda k: abs(cs[k]))
    p = perm_p(d[best].values, d[t].values)
    p_adj = min(1, p * len(X))  # we looked at every feature: Bonferroni
    pred = np.zeros(len(d))
    Z = (d[X] - d[X].mean()) / d[X].std()
    for i in range(len(d)):
        m = np.arange(len(d)) != i
        pred[i] = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(Z[m], d[t].values[m]).predict(Z.iloc[[i]])[0]
    loo = spearmanr(pred, d[t]).statistic
    out.append(f"| {t} | {kind} | {best} | {cs[best]:+.2f} | {p:.3f} (adj. {p_adj:.2f}) | {loo:+.2f} |")
out += ["", "## All correlations (rank)", "", "| Path feature | " + " | ".join(TARGETS) + " |",
        "|---|" + "---|" * len(TARGETS)]
for x in X:
    out.append(f"| {x} | " + " | ".join(f"{spearmanr(df[x], df[t], nan_policy='omit').statistic:+.2f}" for t in TARGETS) + " |")
os.makedirs("results/sperm", exist_ok=True)
open("results/sperm/PATHS.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
