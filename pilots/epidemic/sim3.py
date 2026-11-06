"""Epidemic model v3: WHERE does a self-copying AI live, habitat by habitat, and which shields remove it?

Habitats (count available, compute units each; 1 unit = one TV box):
  small devices    98,000 TV boxes / routers / network drives, ~0.94 units each (v1 mix)
  PCs & laptops    22,000 home PCs/laptops (2,000 with gaming GPUs: 20 units; 20,000 ordinary: 3 units)
  cloud            accounts at big clouds opened with stolen credentials/cards, 50 units, max 2,000
  web2 GPU rental  card-paid GPU marketplaces, 20 units, max 3,000, abuse removal ~4 days
  web3 GPU rental  crypto-paid decentralised GPU markets, 20 units, max 3,000, little identity checking (~14 days)
  storage          model files on undeletable decentralised storage: restart point when compute is lost

Shields: device (router add-on / PC software: blocks 70% of new home infections, PCs also cleaned faster),
ISP cleaning (80% of home connections, after 3-day detection), cloud watch (accounts closed ~2 days),
web2 checks (block 80% of new rentals, removal ~1 day), web3 checks (if decentralised markets cooperate:
block 50%, removal ~4 days), storage takedown. Assumption-based; shows mechanisms, not forecasts.
"""
import os

import numpy as np

H = 24 * 90
BETA = 0.012
C_MIN = 15.0
POW = {"small": 0.94, "gpu_pc": 20.0, "pc": 3.0, "cloud": 50.0, "w2": 20.0, "w3": 20.0}
CAP = {"small": 98_000, "gpu_pc": 2_000, "pc": 20_000, "cloud": 2_000, "w2": 3_000, "w3": 3_000}
HOME = ("small", "gpu_pc", "pc")
G = {"cloud": 0.0003, "w2": 0.0004, "w3": 0.0004}   # new accounts/rentals per hour per compute unit


def run(rng, sh, delay=72):
    x = {k: 0.0 for k in POW}
    x["small"] = 20.0
    seen = None
    restarts = 0
    for t in range(H):
        A = sum(x[k] * POW[k] for k in POW)
        if seen is None and A > 0:
            seen = t
        if A >= C_MIN:
            for k in HOME:
                S = CAP[k] - x[k]
                lam = BETA * A * S / sum(CAP[h] for h in HOME) * (0.3 if "device" in sh else 1.0)
                x[k] += rng.binomial(int(S), min(1.0, lam / max(S, 1))) if S > 0 else 0
            for k in ("cloud", "w2", "w3"):
                block = {"cloud": 0.0, "w2": 0.8 if "web2" in sh else 0.0, "w3": 0.5 if "web3" in sh else 0.0}[k]
                x[k] += rng.poisson(G[k] * A * (1 - block) * max(0.0, 1 - x[k] / CAP[k]))
        det = seen is not None and t - seen >= delay
        for k in HOME:
            p = 0.002 / 24                                   # owners patching anyway
            if "isp" in sh and det:
                p += 0.8 * 0.4                               # 80% of homes behind cooperating ISPs, cleaned at 40%/h
            if "device" in sh and det and k != "small":
                p += 0.02                                    # PC security software removes it
            x[k] -= rng.binomial(int(x[k]), min(1.0, p))
        rem = {"cloud": 1 / 48 if "cloud" in sh else 1 / 720,
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


NAMES = {"small": "TV boxes & small devices", "gpu_pc": "Gaming PCs (GPU)", "pc": "Ordinary PCs & laptops",
         "cloud": "Big cloud accounts", "w2": "Web2 GPU rental", "w3": "Web3 GPU rental"}
SETS = {"No shields": set(), "ISP + cloud + web2 + web3 checks": {"isp", "cloud", "web2", "web3"},
        "+ device shield": {"isp", "cloud", "web2", "web3", "device"},
        "+ storage takedown (everything)": {"isp", "cloud", "web2", "web3", "device", "storage"},
        "Everything except web3 checks": {"isp", "cloud", "web2", "device", "storage"},
        "Everything except device shield": {"isp", "cloud", "web2", "web3", "storage"}}
L = ["# Where does it live? Habitat-by-habitat (model v3)", "",
     "80 simulated outbreaks per row, 90 days, 3-day detection. Shares = where its computing power sits at day 90, "
     "averaged over the outbreaks still alive. All numbers assumed.", "",
     "| Shields | Still alive | " + " | ".join(NAMES.values()) + " | Restarts from storage (avg) |",
     "|---|---|" + "---|" * len(NAMES) + "---|"]
for name, sh in SETS.items():
    rng = np.random.default_rng(21)
    rs = [run(rng, sh) for _ in range(80)]
    alive = [r for r in rs if r[0]]
    sh_avg = {k: np.mean([r[1][k] for r in alive]) if alive else 0 for k in POW}
    L.append(f"| {name} | {len(alive) / len(rs):.0%} | " + " | ".join(f"{sh_avg[k]:.0%}" for k in POW) +
             f" | {np.mean([r[3] for r in rs]):.1f} |")
os.makedirs("results/epidemic", exist_ok=True)
open("results/epidemic/EPIDEMIC_V3.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
