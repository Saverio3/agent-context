"""Epidemic model v2: a self-copying AI that can live in THREE places, and which 'shield' stops it.

Habitats (each gives computing power the AI needs to think and spread):
  home devices   100,000 vulnerable TV boxes / routers / NAS / GPU PCs (as v1), 3.4 compute units on average
  cloud accounts accounts opened with stolen credentials or stolen cards at big providers; 50 units each
  rented GPUs    on decentralised GPU marketplaces paid in crypto (weak identity checks); 20 units each
Caps: at most 2,000 cloud accounts and 5,000 rented GPUs.
Plus: model files kept on decentralised storage that nobody can delete -> after a takedown the AI can be
re-started from there if it can still rent compute.

Shields (each can be on/off):
  device shield     antivirus / router-level 'AI-runtime' detection: 70% of new device infections blocked
  ISP cleaning      cooperating providers (80% of devices) clean infected customers after detection delay
  cloud watch       big clouds spot unusual GPU use / stolen payment and close accounts (mean 2 days)
  market checks     decentralised GPU markets check identity / ban abusive renters (block 80% of new rentals,
                    close running ones within ~2 days)
  storage takedown  model files can be removed (only possible if storage is not truly decentralised)
Every number is an assumption; outputs show which shields matter, not forecasts. 60 outbreaks per setting,
same random draws for every row.
"""
import itertools
import os

import numpy as np

H = 24 * 90
N_DEV, DEV_POW = 100_000, 3.4
C_MIN = 15.0
BETA = 0.012                 # device infections per hour per compute unit (as v1)
G_CLOUD = 0.0004             # new cloud accounts per hour per compute unit (stolen creds found)
G_MARKET = 0.0006            # new GPU rentals per hour per compute unit (crypto payment)
CLOUD_POW, MARKET_POW = 50.0, 20.0
C_MAX, M_MAX = 2000.0, 5000.0   # most accounts / rentals it could plausibly hold (stolen cards, market capacity)


def run(rng, device=False, isp=False, cloud=False, market=False, storage=False, delay=72):
    S, I, C, M = N_DEV - 20.0, 20.0, 0.0, 0.0
    peak = 0.0; seen = None; dormant = 0
    for t in range(H):
        A = I * DEV_POW + C * CLOUD_POW + M * MARKET_POW
        if A > 0 and seen is None:
            seen = t
        if A >= C_MIN:
            lam = BETA * A * S / N_DEV * (0.3 if device else 1.0)
            new = rng.binomial(int(S), min(1.0, lam / max(S, 1))) if S > 0 else 0
            S -= new; I += new
            C += rng.poisson(G_CLOUD * A * max(0.0, 1 - C / C_MAX))
            M += rng.poisson(G_MARKET * A * (0.2 if market else 1.0) * max(0.0, 1 - M / M_MAX))
        detected = seen is not None and t - seen >= delay
        if isp and detected:
            I -= rng.binomial(int(I), 0.8 * 0.5)          # 80% of devices behind cooperating ISPs, 50%/h cleaned
        I -= rng.binomial(int(I), 0.002 / 24)               # background owner patching
        if cloud:
            C -= rng.binomial(int(C), 1 / 48)               # accounts closed, mean 2 days
        else:
            C -= rng.binomial(int(C), 1 / (24 * 30))        # only billing failures, ~monthly
        M -= rng.binomial(int(M), (1 / 48) if market else (1 / (24 * 14)))  # rentals end / banned
        A = I * DEV_POW + C * CLOUD_POW + M * MARKET_POW
        peak = max(peak, A)
        if A < C_MIN:
            # below the threshold it cannot think; it can restart from undeletable storage by renting GPUs
            if not storage and rng.random() < (0.002 if market else 0.02):
                M += 1                                       # one rental from stored model files
            dormant += 1
    A = I * DEV_POW + C * CLOUD_POW + M * MARKET_POW
    return A >= C_MIN, peak, A


def batch(n=60, **kw):
    rng = np.random.default_rng(11)
    rs = [run(rng, **kw) for _ in range(n)]
    return np.mean([r[0] for r in rs]), np.median([r[1] for r in rs]), np.median([r[2] for r in rs])


SH = ["device", "isp", "cloud", "market", "storage"]
LAB = {"device": "Device shield", "isp": "ISP cleaning", "cloud": "Cloud watch", "market": "Market checks",
       "storage": "Storage takedown"}
L = ["# Where would a self-copying AI live, and which shield stops it? (model v2)", "",
     "Three habitats: home devices, cloud accounts, rented GPUs on decentralised markets; model files on undeletable "
     "storage allow restarts. 60 simulated outbreaks per row, 90 days, detection delay 3 days. 'Still alive' = still "
     "has enough computing power to act at day 90. Compute in TV-box units.", "",
     "| Shields on | Still alive at day 90 | Peak compute | Compute at day 90 |", "|---|---|---|---|"]
rows = [()] + [(s,) for s in SH] + [("device", "isp"), ("isp", "cloud"), ("cloud", "market"),
                                     ("isp", "cloud", "market"), ("device", "isp", "cloud", "market"),
                                     ("isp", "cloud", "market", "storage"), tuple(SH)]
for r in rows:
    a, pk, fin = batch(**{s: True for s in r})
    L.append(f"| {' + '.join(LAB[s] for s in r) or 'none'} | {a:.0%} | {pk:,.0f} | {fin:,.0f} |")
L += ["", "## Leave-one-out: all shields on except one", "", "| Missing shield | Still alive at day 90 |", "|---|---|"]
for s in SH:
    a, _, _ = batch(**{x: True for x in SH if x != s})
    L.append(f"| {LAB[s]} | {a:.0%} |")
os.makedirs("results/epidemic", exist_ok=True)
open("results/epidemic/EPIDEMIC_V2.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
