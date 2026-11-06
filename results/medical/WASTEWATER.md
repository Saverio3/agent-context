# Wastewater → hospital admissions (space-time nowcast)

Train: weeks before 2025-07-01 · test: weeks after (out-of-sample). Error = mean absolute error of log(admissions+1), roughly the typical % miss. Direction = share of state-weeks where the model called rise vs fall correctly (persistence can't call direction, so it's blank).

| Disease | Weeks ahead | Test state-weeks | A: same as this week | B: + admission trend | C: + own sewage | D: + neighbours' sewage | Gain D vs B | Direction B → D |
|---|---|---|---|---|---|---|---|---|
| COVID | 1 | 3,345 | 0.291 | 0.288 | 0.284 | 0.278 | +3.3% | 55% → 61% |
| COVID | 2 | 3,296 | 0.372 | 0.370 | 0.363 | 0.351 | +5.0% | 55% → 63% |
| Flu A | 1 | 3,181 | 0.383 | 0.388 | 0.382 | 0.376 | +3.0% | 51% → 60% |
| Flu A | 2 | 3,134 | 0.528 | 0.526 | 0.517 | 0.506 | +3.8% | 51% → 60% |
| RSV | 1 | 2,882 | 0.382 | 0.387 | 0.386 | 0.386 | +0.4% | 52% → 54% |
| RSV | 2 | 2,846 | 0.469 | 0.490 | 0.486 | 0.481 | +1.8% | 50% → 54% |

## Does sewage move first?

Correlation between this week's change in sewage and the change in admissions k weeks later (all states, all weeks). Peak at k > 0 means sewage leads.

| Disease | k=0 | k=1 | k=2 | k=3 |
|---|---|---|---|---|
| COVID | 0.10 | 0.10 | 0.10 | 0.07 |
| Flu A | 0.16 | 0.13 | 0.11 | 0.07 |
| RSV | 0.07 | 0.04 | 0.06 | 0.04 |
