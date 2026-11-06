"""Pilot: WHO carries extra risk from fertility treatment? (US birth certificates, 2023)

Data: CDC/NCHS 2023 natality public-use file (every US birth; fixed width, positions from the 2023 User Guide).
Singletons only (twins are a known, separate pathway). Treatment: infertility treatment used (RF_INFTR = Y);
also split into ART (IVF etc.) vs fertility drugs only.
Outcomes: preterm (<37 wk), low birth weight (<2500 g), NICU admission, 5-min Apgar < 7, caesarean.
Pre-pregnancy covariates only (no mediators like gestational diabetes).

Steps
 1. Average adjusted effect (double machine learning, AIPW) per outcome.
 2. DR-learner (gradient-boosted model of the doubly-robust scores) on half the data -> predicted individual extra risk.
 3. Honest check on the OTHER half: sort mothers by predicted extra risk into quartiles and estimate
    the real effect inside each quartile (AIPW). If the top quartile really has a bigger effect than the
    bottom, the heterogeneity is real, not overfitting.
 4. What drives it: features most associated with predicted extra risk.
Caveat: infertility itself (not just treatment) may raise risks; birth-certificate treatment flag is
under-reported. These are associations adjusted for measured factors, not proof of cause.
"""
import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import KFold

F = {"mager": (75, 76), "mrace6": (107, 107), "meduc": (124, 124), "dmar": (120, 120), "pay": (435, 435),
     "lbo": (179, 179), "bmi": (283, 286), "cig0": (253, 254), "pdiab": (313, 313), "phype": (315, 315),
     "ppterm": (318, 318), "cesar_prev": (331, 331), "precare": (224, 225), "inftr": (325, 325),
     "fedrg": (326, 326), "artec": (327, 327), "plural": (454, 454), "sex": (475, 475), "gest": (490, 491),
     "bwt": (504, 507), "apgar5": (444, 445), "nicu": (519, 519), "route": (402, 402)}
path = sys.argv[1]
N_CTRL = int(os.environ.get("N_CTRL", "400000"))
cols = [(a - 1, b) for a, b in F.values()]
data = {k: [] for k in F}
with open(path, encoding="latin-1") as fh:
    for line in fh:
        for k, (a, b) in zip(F, cols):
            data[k].append(line[a:b].strip())
d = pd.DataFrame(data)
del data
print("births", len(d), flush=True)
d = d[(d.plural == "1") & d.inftr.isin(["Y", "N"])].copy()
num = lambda c, bad: pd.to_numeric(d[c], errors="coerce").where(lambda s: ~s.isin(bad))
d["age"] = num("mager", []); d["bmi_"] = num("bmi", [99.9]); d["cig"] = num("cig0", [99])
d["parity"] = num("lbo", [9]); d["care"] = num("precare", [99]); d["edu"] = num("meduc", [9])
d["gest_"] = num("gest", [99]); d["bwt_"] = num("bwt", [9999]); d["ap5"] = num("apgar5", [99])
for c in ("pdiab", "phype", "ppterm", "cesar_prev"):
    d[c + "_y"] = (d[c] == "Y").astype(float)
d["married"] = (d.dmar == "1").astype(float); d["medicaid"] = (d.pay == "1").astype(float)
d["private"] = (d.pay == "2").astype(float); d["male"] = (d.sex == "M").astype(float)
for k in range(1, 7):
    d[f"race{k}"] = (d.mrace6 == str(k)).astype(float)
d["T"] = (d.inftr == "Y").astype(int)
d["T_art"] = (d.artec == "Y").astype(int)
Y = {"Preterm (<37 wk)": (d.gest_ < 37), "Low birth weight": (d.bwt_ < 2500), "NICU admission": (d.nicu == "Y"),
     "Apgar5 < 7": (d.ap5 < 7), "Caesarean": (d.route == "4")}
valid = d.gest_.notna() & d.bwt_.notna() & d.ap5.notna() & d.nicu.isin(["Y", "N"]) & (d.route != "9")
d = d[valid]
for k, v in Y.items():
    d[k] = v[valid].astype(int)
X = ["age", "bmi_", "cig", "parity", "care", "edu", "pdiab_y", "phype_y", "ppterm_y", "cesar_prev_y", "married",
     "medicaid", "private", "male"] + [f"race{k}" for k in range(1, 7)]
d = d.dropna(subset=X)
treated = d[d["T"] == 1]
ctrl = d[d["T"] == 0].sample(min(N_CTRL, (d["T"] == 0).sum()), random_state=0)
w_ctrl = (d["T"] == 0).sum() / len(ctrl)  # reweight sampled controls back to population
D = pd.concat([treated, ctrl]).sample(frac=1, random_state=1).reset_index(drop=True)
D["w"] = np.where(D["T"] == 1, 1.0, w_ctrl)
print("singletons used", len(d), "treated", len(treated), f"({len(treated)/len(d):.2%})", "ART", int(treated.T_art.sum()), flush=True)


def gbm():
    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, max_leaf_nodes=31, random_state=0)


def aipw_scores(df, y):
    """Cross-fitted AIPW pseudo-outcomes for the treatment effect (risk difference)."""
    psi = np.zeros(len(df))
    for tr, te in KFold(3, shuffle=True, random_state=0).split(df):
        a, b = df.iloc[tr], df.iloc[te]
        e = gbm().fit(a[X], a["T"]).predict_proba(b[X])[:, 1].clip(0.002, 0.998)
        m1 = gbm().fit(a[a["T"] == 1][X], a[a["T"] == 1][y]).predict_proba(b[X])[:, 1]
        m0 = gbm().fit(a[a["T"] == 0][X], a[a["T"] == 0][y]).predict_proba(b[X])[:, 1]
        t, yy = b["T"].values, b[y].values
        # population-weighted propensity: controls were subsampled, so rescale odds
        e_pop = e / (e + (1 - e) * w_ctrl)
        psi[te] = m1 - m0 + t * (yy - m1) / e_pop - (1 - t) * (yy - m0) / (1 - e_pop)
    return psi


def wmean(x, w):
    m = np.average(x, weights=w); se = np.sqrt(np.average((x - m) ** 2, weights=w) / len(x)) * np.sqrt(len(x) * (w ** 2).sum() / w.sum() ** 2)
    return m, se


out = ["# Who carries extra risk from fertility treatment? (US births 2023, singletons)", "",
       f"Singleton births analysed: {len(d):,}; fertility treatment: {len(treated):,} ({len(treated)/len(d):.1%}), of which ART "
       f"(IVF etc.) {int(treated.T_art.sum()):,}. Controls subsampled to {len(ctrl):,} and reweighted. "
       "Effects are risk differences in percentage points, adjusted for pre-pregnancy factors "
       "(age, BMI, smoking, parity, prior preterm, prior caesarean, diabetes, hypertension, education, insurance, marital status, race, prenatal care, baby sex).", "",
       "| Outcome | Rate if untreated | Raw gap | Adjusted extra risk (pp) | Lowest-risk quarter of mothers | Highest-risk quarter | Top vs bottom (pp) |",
       "|---|---|---|---|---|---|---|"]
drivers = []
from sklearn.ensemble import HistGradientBoostingRegressor
for y in Y:
    psi = aipw_scores(D, y)
    ate, se = wmean(psi, D.w.values)
    base = np.average(D[D["T"] == 0][y], weights=D[D["T"] == 0].w)
    raw = D[D["T"] == 1][y].mean() - base
    # heterogeneity: fit forest on half A, evaluate quartiles on half B with AIPW scores (honest)
    half = np.random.default_rng(2).random(len(D)) < 0.5
    A, B = D[half], D[~half]
    # DR-learner: regress the doubly-robust scores on mothers' characteristics (half A only)
    cf = HistGradientBoostingRegressor(max_iter=150, learning_rate=0.05, min_samples_leaf=500, random_state=0)
    cf.fit(A[X].values, psi[half], sample_weight=A.w.values)
    tau_B = cf.predict(B[X].values)
    q = pd.qcut(tau_B, 4, labels=False, duplicates="drop")
    qe = [wmean(psi[~half][q == k], B.w.values[q == k]) for k in range(int(q.max()) + 1)]
    lo, hi = qe[0], qe[-1]
    diff = hi[0] - lo[0]; dse = np.sqrt(hi[1] ** 2 + lo[1] ** 2)
    out.append(f"| {y} | {base:.1%} | {raw*100:+.2f} | **{ate*100:+.2f}** (±{1.96*se*100:.2f}) | {lo[0]*100:+.2f} (±{1.96*lo[1]*100:.2f}) | "
               f"{hi[0]*100:+.2f} (±{1.96*hi[1]*100:.2f}) | {diff*100:+.2f} (±{1.96*dse*100:.2f}) |")
    corr = {x: np.corrcoef(B[x].values, tau_B)[0, 1] for x in X if B[x].std() > 0}
    top = sorted(corr.items(), key=lambda kv: -abs(kv[1]))[:4]
    drivers.append(f"- **{y}**: " + ", ".join(f"{k} ({v:+.2f})" for k, v in top))
    print(y, "done", flush=True)
out += ["", "Quarters: mothers sorted by the model's predicted extra risk (fitted on one half), effect then measured on the "
        "other half — so a real top-vs-bottom gap is not overfitting. ± = 95% interval.", "",
        "## What drives the extra risk (correlation with predicted extra risk)", ""] + drivers
os.makedirs("results/natality", exist_ok=True)
open("results/natality/NATALITY.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
