"""Epidemic model for a self-replicating AI ('AI worm') on cheap internet devices.

Built on Anthropic's Oct 2026 red-team result: small models can run split across cheap devices
(a 26B model across 15 TV boxes) and stronger models can replicate end-to-end.

World: 50 internet providers (sizes very unequal), 100,000 vulnerable devices of 4 kinds with different
computing power. A worm only 'thinks' (scans and breaks into new devices) when its infected devices add up
to enough computing power; more power -> faster spread. Providers that cooperate detect it after a delay,
clean infected customers and filter incoming attacks. Some providers never cooperate.
Every number is an assumption; the point is which levers matter, not exact forecasts.
"""
import itertools, os, sys
import numpy as np

TYPES = {  # name: (count, compute units each)
    "TV box": (70000, 1.0), "router": (20000, 0.3), "NAS": (8000, 2.0), "gaming PC / GPU box": (2000, 20.0)}
NAMES = list(TYPES)
COUNT = np.array([TYPES[t][0] for t in NAMES], float)
POWER = np.array([TYPES[t][1] for t in NAMES])
P, HOURS = 50, 24 * 90
C_MIN = 15.0          # compute units needed before the worm can act (15 TV boxes)
BETA = 0.012         # infections per hour per compute unit: unchecked worm reaches half its peak in ~3 weeks


def world(rng):
    share = 1 / np.arange(1, P + 1) ** 1.1; share /= share.sum()
    S = np.outer(share, COUNT)                              # susceptible devices per provider x type
    return np.floor(S + rng.random(S.shape)), share


def run(rng, coop=1.0, delay=24, clean=0.5, filt=0.9, patch_day=0.002, protect=None, protect_share=0.0, seeds=20):
    S, share = world(rng)
    N0 = S.sum()                                             # fixed size of the reachable device population
    if protect is not None:                                  # e.g. vendors patch one device class up front
        S[:, protect] = np.floor(S[:, protect] * (1 - protect_share))
    I = np.zeros_like(S)
    src = rng.choice(P, p=share)
    I[src, 0] = seeds; S[src, 0] -= seeds
    cooperates = rng.random(P) < coop
    first_seen = np.full(P, -1)
    detected = np.zeros(P, bool)
    peak, hist = 0, []
    for t in range(HOURS):
        inf_p = I.sum(1)
        first_seen[(first_seen < 0) & (inf_p > 0)] = t
        detected |= cooperates & (first_seen >= 0) & (t - first_seen >= delay)
        A = (I * POWER).sum()
        if A >= C_MIN:
            # attacks land on providers in proportion to their susceptible devices; filtered at detected providers
            pressure = BETA * A
            w = S.sum(1) * np.where(detected, 1 - filt, 1.0)
            tot_s = S.sum()
            if tot_s > 0:
                lam = pressure * (w / max(1.0, N0))[:, None] * (S / np.maximum(S.sum(1, keepdims=True), 1))
                new = rng.binomial(S.astype(int), np.clip(lam / np.maximum(S, 1), 0, 1))
                S -= new; I += new
        # cleaning at detected providers, background patching everywhere
        cl = rng.binomial(I.astype(int), np.where(detected, clean, 0.0)[:, None] * np.ones_like(I))
        I -= cl
        I -= rng.binomial(I.astype(int), patch_day / 24)
        S -= rng.binomial(S.astype(int), patch_day / 24)
        tot = I.sum(); peak = max(peak, tot)
        if t % 24 == 0: hist.append(tot)
        if tot == 0: return dict(eradicated=True, active=False, peak=peak, final=0, day=t / 24, hist=hist)
    return dict(eradicated=False, active=(I * POWER).sum() >= C_MIN, peak=peak, final=I.sum(), day=HOURS / 24, hist=hist)


def batch(n=30, seed=0, **kw):
    rng = np.random.default_rng(seed)
    rs = [run(rng, **kw) for _ in range(n)]
    return (np.mean([r["active"] for r in rs]), np.median([r["peak"] for r in rs]),
            np.median([r["final"] for r in rs]), np.mean([r["eradicated"] for r in rs]), rs)


def main(out="results/epidemic"):
    os.makedirs(out, exist_ok=True)
    L = ["# Epidemic model for a self-replicating AI on cheap devices", "",
         "100,000 vulnerable devices across 50 internet providers; worm needs 15 TV-box-equivalents of computing "
         "power before it can spread; 60-80 simulated outbreaks per setting (same random worlds for every option, so rows are directly comparable), 90 days each. All numbers are assumptions.", ""]
    e, pk, fin, _, rs = batch(coop=0.0, n=10)
    days_half = np.median([next((d for d, v in enumerate(r["hist"]) if v >= 0.5 * pk), np.nan) for r in rs])
    L += [f"**No defence:** peak {pk:,.0f} infected devices; half of that reached by day {days_half:.0f}.", ""]

    L += ["## 1. How fast must providers act, and how many must cooperate?", "",
          "Cells: chance the worm is STILL ABLE TO SPREAD at day 90 · infected devices left at day 90 (median). "
          "(Below 15 TV-box-equivalents the leftover infected devices cannot act.)", "",
          "| Detection delay | 100% of providers | 99% | 95% | 80% | 50% |", "|---|---|---|---|---|---|"]
    grid = {}
    for d in (1, 6, 24, 72, 168):
        cells = []
        for c in (1.0, 0.99, 0.95, 0.8, 0.5):
            e, pk, fin, dd, _ = batch(n=60, coop=c, delay=d, seed=7)
            grid[(d, c)] = (e, pk, fin)
            cells.append(f"{e:.0%} · {fin:,.0f}")
        L.append(f"| {d} h | " + " | ".join(cells) + " |")

    L += ["", "## 2. Which devices matter most? (patch 50% of one device class before the outbreak; bad-case world: 80% of providers cooperate, 1-week detection)", "",
          "| Patched class | Still spreading at day 90 | Peak infected | Left at day 90 |", "|---|---|---|---|"]
    base = batch(n=80, coop=0.8, delay=168, seed=7)
    L.append(f"| none | {base[0]:.0%} | {base[1]:,.0f} | {base[2]:,.0f} |")
    for k, name in enumerate(NAMES):
        r = batch(n=80, coop=0.8, delay=168, protect=k, protect_share=0.5, seed=7)
        L.append(f"| {name} ({TYPES[name][0]:,} devices) | {r[0]:.0%} | {r[1]:,.0f} | {r[2]:,.0f} |")

    L += ["", "## 3. Which response matters most? (same bad-case world: 80% cooperate, 1-week detection)", "",
          "| Response | Still spreading at day 90 | Peak | Left at day 90 |", "|---|---|---|---|"]
    for lab, kw in [("Clean 50% of infected per hour + filter 90% of incoming (baseline)", {}),
                    ("Clean only (no filtering)", dict(filt=0.0)),
                    ("Filter only (no cleaning)", dict(clean=0.0)),
                    ("Slow cleaning (10%/hour)", dict(clean=0.1)),
                    ("Faster owner patching (2%/day instead of 0.2%)", dict(patch_day=0.02))]:
        r = batch(n=80, coop=0.8, delay=168, seed=7, **kw)
        L.append(f"| {lab} | {r[0]:.0%} | {r[1]:,.0f} | {r[2]:,.0f} |")
    open(os.path.join(out, "EPIDEMIC.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
