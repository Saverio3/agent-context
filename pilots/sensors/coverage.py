"""eBird-for-agents: how many installed sensors are needed to (a) spot a new AI-agent campaign and
(b) name the AI model behind it, and how fast?

Assumptions (stated, adjustable): a campaign probes random addresses among ~3.7 billion public IPv4 addresses;
each sensor is one address. A single sighting identifies the model family with 85% accuracy (our fingerprint
pilot, whole-run evidence, 10 models); several sightings are combined by majority vote, errors spread over the
other 9 models."""
import math, os
import numpy as np

SPACE = 3.7e9
ACC, K = 0.85, 10


def vote_accuracy(n, trials=20000, rng=np.random.default_rng(0)):
    if n == 0: return 0.0
    correct = rng.random((trials, n)) < ACC
    wrong = rng.integers(1, K, (trials, n))
    labels = np.where(correct, 0, wrong)
    ok = 0
    for row in labels:
        c = np.bincount(row, minlength=K)
        ok += c[0] == c.max() and (c == c.max()).sum() == 1 or (c[0] == c.max() and rng.random() < 1 / (c == c.max()).sum())
    return ok / trials


def main():
    rates = {"stealthy (1,000 probes/h)": 1e3, "moderate (100,000/h)": 1e5, "aggressive (10 million/h)": 1e7}
    L = ["# eBird for agents: how many sensors are needed?", "",
         "Time until the network has 5 sightings of a new AI-agent campaign (enough to name the model ~"
         f"{vote_accuracy(5):.0%} of the time by majority vote; 1 sighting: {ACC:.0%}, 3: {vote_accuracy(3):.0%}, 9: {vote_accuracy(9):.0%}).", "",
         "| Installed sensors | " + " | ".join(rates) + " |", "|---|" + "---|" * len(rates)]
    def fmt(h):
        if h < 1: return f"{h * 60:.0f} min"
        if h < 48: return f"{h:.0f} h"
        if h < 24 * 60: return f"{h / 24:.0f} days"
        return f"{h / 24 / 365:.1f} years"
    for n in (100, 1_000, 10_000, 100_000, 1_000_000):
        cells = [fmt(5 / (r * n / SPACE)) for r in rates.values()]
        L.append(f"| {n:,} | " + " | ".join(cells) + " |")
    L += ["", "Caveat: the vote assumes each sighting's error is independent; in reality errors on one campaign are "
          "correlated, so treat the naming figures as optimistic.", "",
          "Reading: a home/office app reaching 100k installs would "
          "spot even a moderate campaign within hours; stealthy campaigns need either huge installs or sensors placed "
          "where the campaign is looking (e.g. on the device types it targets)."]
    os.makedirs("results/sensors", exist_ok=True)
    open("results/sensors/COVERAGE.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
