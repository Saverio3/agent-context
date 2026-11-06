"""Does the video add anything beyond the standard lab semen analysis? (VISEM, 85 men)
Leave-one-man-out ridge on log(hormone): A = standard semen analysis (concentration, total count,
progressive & non-progressive motility, immotile, normal morphology, volume); B = video features only;
C = A + video. Score: rank correlation of predictions with truth; bootstrap 95% interval for C - A."""
import glob, numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
R = "data/visem/full/visem-dataset"
rd = lambda f: pd.read_csv(f"{R}/{f}", sep=";", encoding="utf-8-sig", decimal=",")
V = pd.read_csv("results/sperm/video_features_raw.csv").groupby("ID").mean(numeric_only=True).reset_index()
S = rd("semen_analysis_data.csv"); H = rd("sex_hormones.csv")
S.columns = ["ID"] + list(S.columns[1:]); H.columns = ["ID"] + list(H.columns[1:])
keepS = [c for c in S.columns if any(k in c for k in ("concentration", "Total sperm count", "Ejaculate volume", "Progressive", "Non progressive", "Immotile", "Normal spermatozoa"))]
D = V.merge(S[["ID"] + keepS], on="ID").merge(H, on="ID")
for c in keepS + list(H.columns[1:]): D[c] = pd.to_numeric(D[c], errors="coerce")
vf = [c for c in V.columns if c != "ID"]
def loo(cols, y):
    d = D.dropna(subset=cols + [y]); Z = (d[cols] - d[cols].mean()) / d[cols].std().replace(0, 1); t = np.log1p(d[y].clip(lower=0)).values
    p = np.array([RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(Z.drop(Z.index[i]), np.delete(t, i)).predict(Z.iloc[[i]])[0] for i in range(len(d))])
    return p, t
out = ["# Does the video add anything beyond the standard semen analysis?", "",
       f"{len(D)} men. Leave-one-man-out; rank correlation of predicted vs true hormone level (log). Bootstrap 95% interval for the gain.", "",
       "| Hormone | Standard semen analysis | Video only | Both | Gain from adding video |", "|---|---|---|---|---|"]
rng = np.random.default_rng(0)
for y in H.columns[1:]:
    pa, t = loo(keepS, y); pb, _ = loo(vf, y); pc, _ = loo(keepS + vf, y)
    g = [spearmanr(pc[i], t[i]).statistic - spearmanr(pa[i], t[i]).statistic for i in (rng.integers(0, len(t), len(t)) for _ in range(1000))]
    out.append(f"| {y.split(' (')[0]} | {spearmanr(pa,t).statistic:+.2f} | {spearmanr(pb,t).statistic:+.2f} | {spearmanr(pc,t).statistic:+.2f} | "
               f"{spearmanr(pc,t).statistic-spearmanr(pa,t).statistic:+.2f} ({np.percentile(g,2.5):+.2f} to {np.percentile(g,97.5):+.2f}) |")
open("results/sperm/HORMONES_ADDON.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))
