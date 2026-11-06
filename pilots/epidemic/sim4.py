"""Epidemic model v4: v3 recalibrated with REAL numbers where they exist, plus sensitivity grids.

Real inputs:
  ISP cleanup      Mirai field study (Cetin et al., NDSS 2019, Dutch ISP): walled-garden quarantine + notice cleaned
                   92% within 14 days (-> 0.75%/hour); without notice 58-74% cleaned naturally (we use ~58% per month,
                   0.12%/hour); email-only notices no effect; only 5% of cleaned devices re-infected (95% become immune).
  spread speed     Mirai's early doubling time was ~76 minutes (Antonakakis et al., USENIX Security 2017). An AI worm
                   must also move gigabytes of model files, so we test three speeds: Mirai-fast (76 min doubling),
                   medium (6 h), slow (60 h, as in v1-v3).
  device reach     Anthropic (Oct 2026): a model got itself running on 8 of 9 tested device types -> most cheap device
                   types count as vulnerable.
Still assumed (no public data): cloud / GPU-market takedown speeds and how fast stolen accounts are opened ->
tested as ranges. Detection delay tested at 1, 3, 7, 14 days.
"""
import os

import numpy as np

H = 24 * 90
BETA = 0.012
ISP_RATE, NATURAL = 0.0075, 0.0012
IMMUNE = 0.95
C_MIN = 15.0
POW = {"small": 0.94, "gpu_pc": 20.0, "pc": 3.0, "cloud": 50.0, "w2": 20.0, "w3": 20.0}
CAP = {"small": 98_000, "gpu_pc": 2_000, "pc": 20_000, "cloud": 2_000, "w2": 3_000, "w3": 3_000}
HOME = ("small", "gpu_pc", "pc")
G = {"cloud": 0.0003, "w2": 0.0004, "w3": 0.0004}   # new accounts/rentals per hour per compute unit


def run(rng, sh, delay=72, beta=0.012, cloud_days=2.0):
    x = {k: 0.0 for k in POW}
    x["small"] = 20.0
    imm = {k: 0.0 for k in HOME}
    seen = None
    restarts = 0
    for t in range(H):
        A = sum(x[k] * POW[k] for k in POW)
        if seen is None and A > 0:
            seen = t
        if A >= C_MIN:
            for k in HOME:
                S = CAP[k] - x[k] - imm[k]
                lam = beta * A * S / sum(CAP[h] for h in HOME) * (0.3 if "device" in sh else 1.0)
                x[k] += rng.binomial(int(S), min(1.0, lam / max(S, 1))) if S > 0 else 0
            for k in ("cloud", "w2", "w3"):
                block = {"cloud": 0.0, "w2": 0.8 if "web2" in sh else 0.0, "w3": 0.5 if "web3" in sh else 0.0}[k]
                x[k] += rng.poisson(G[k] * A * (1 - block) * max(0.0, 1 - x[k] / CAP[k]))
        det = seen is not None and t - seen >= delay
        for k in HOME:
            p = NATURAL
            if "isp" in sh and det:
                p += 0.8 * ISP_RATE                          # 80% of homes behind cooperating ISPs (walled garden)
            if "device" in sh and det and k != "small":
                p += 0.02                                    # PC security software
            c = rng.binomial(int(x[k]), min(1.0, p))
            x[k] -= c; imm[k] += IMMUNE * c
        rem = {"cloud": 1 / (24 * cloud_days) if "cloud" in sh else 1 / 720,
               "w2": 1 / 24 if "web2" in sh else 1 / 96,
               "w3": 1 / 96 if "web3" in sh else 1 / 336}
        for k, r in rem.items():
            x[k] -= rng.binomial(int(x[k]), r)
        A = sum(x[k] * POW[k] for k in POW)
        if A < C_MIN and "storage" not in sh:
            # restart from stored files by renting GPUs (web3 easiest)
            if rng.random() < (0.004 if "web3" in sh else 0.02):
                x["w3"] += 1; restarts += 1
    A = sum(x[k] * POW[k] for k in POW)
    share = {k: x[k] * POW[k] / A if A > 0 else 0 for k in POW}
    return A >= C_MIN, share, A, restarts


NAMES = {"small": "TV boxes & small devices", "gpu_pc": "Gaming PCs", "pc": "PCs & laptops",
         "cloud": "Big cloud", "w2": "Web2 GPU", "w3": "Web3 GPU"}
ALL = {"isp", "cloud", "web2", "web3", "device", "storage"}
SPEED = {"Mirai-fast (76-min doubling)": 0.58, "Medium (6 h)": 0.12, "Slow (60 h)": 0.012}


def batch(sh, n=60, **kw):
    rng = np.random.default_rng(21)
    rs = [run(rng, sh, **kw) for _ in range(n)]
    alive = [r for r in rs if r[0]]
    share = {k: np.mean([r[1][k] for r in alive]) if alive else 0 for k in POW}
    return len(alive) / len(rs), share


L = ["# Rogue-AI epidemic, recalibrated with real-world numbers (model v4)", "",
     "ISP cleanup from the Mirai field study (walled garden: 92% cleaned in 14 days; 5% re-infection); speeds bracketed by "
     "Mirai's 76-minute doubling. Cloud/GPU-market numbers still assumed. 60 outbreaks per cell, 90 days.", "",
     "## A. All shields on: % still alive at day 90", "",
     "| Spread speed | Detected in 1 day | 3 days | 7 days | 14 days |", "|---|---|---|---|---|"]
for nm, b in SPEED.items():
    L.append(f"| {nm} | " + " | ".join(f"{batch(ALL, beta=b, delay=24 * d)[0]:.0%}" for d in (1, 3, 7, 14)) + " |")
L += ["", "## B. Which shields matter (medium speed, 3-day detection)", "",
      "| Shields | Still alive | " + " | ".join(NAMES.values()) + " |", "|---|---|" + "---|" * len(NAMES)]
rows = {"None": set(), "ISP walled garden only": {"isp"}, "ISP + cloud + web2 + web3 checks": {"isp", "cloud", "web2", "web3"},
        "+ device shield": {"isp", "cloud", "web2", "web3", "device"}, "Everything": ALL,
        "Everything except web3 checks": ALL - {"web3"}, "Everything except device shield": ALL - {"device"},
        "Everything except ISP": ALL - {"isp"}, "Everything except storage takedown": ALL - {"storage"}}
for nm, sh in rows.items():
    a, s = batch(sh, beta=0.12)
    L.append(f"| {nm} | {a:.0%} | " + " | ".join(f"{s[k]:.0%}" for k in POW) + " |")
L += ["", "## C. Cloud takedown speed (everything on, medium speed, 3-day detection)", "", "| Cloud closes accounts in | Still alive |", "|---|---|"]
for cd in (0.5, 2, 7):
    L.append(f"| {cd:g} days | {batch(ALL, beta=0.12, cloud_days=cd)[0]:.0%} |")
os.makedirs("results/epidemic", exist_ok=True)
open("results/epidemic/EPIDEMIC_V4.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))

# D. How easily can it open new cloud/GPU accounts? (the main remaining unknown)
L2 = ["", "## D. How easily it opens new cloud / GPU accounts (everything on, medium speed, 3-day detection, cloud 2 days)", "",
      "| Account-opening rate vs baseline | Still alive |", "|---|---|"]
base = dict(G)
for f in (0.05, 0.1, 0.3, 1.0):
    for k in G:
        G[k] = base[k] * f
    L2.append(f"| {f:g}x | {batch(ALL, beta=0.12)[0]:.0%} |")
G.update(base)
open("results/epidemic/EPIDEMIC_V4.md", "a").write("\n".join(L2) + "\n")
print("\n".join(L2))
