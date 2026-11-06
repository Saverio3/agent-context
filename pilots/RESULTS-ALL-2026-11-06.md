# All pilots: results and ranking (6 Nov 2026)

Code and raw outputs: GitHub repo Saverio3/agent-context (`pilots/`, `results/`).

## 1. eBird for agents (spot and name AI agents in the wild)

### 1a. Fingerprint: which AI model is it?
4,964 real coding-agent runs, 10 models; tested on tasks never seen in training.

| Evidence seen | Accuracy (guessing = 10%) |
|---|---|
| First 3 steps | 59% |
| First half of run | 74% |
| Whole run | 85% |

| Can we predict its next move? | Next command right |
|---|---|
| Generic predictor | 37.8% |
| Using the fingerprinted model | 38.2% |
| Knowing the true model | 38.8% |

→ Identifies the model well (Claude Opus 97–98%, GLM-5 69%). Knowing the model does not help predict what it does next.

### 1b. Sensors: how many are needed? (maths, not data)

| Sensors | Stealthy agent (5 sightings) | Moderate | Aggressive |
|---|---|---|---|
| 1,000 | 2.1 years | 8 days | 2 h |
| 10,000 | 0.2 years | 18 h | 11 min |
| 100,000 | 8 days | 2 h | 1 min |

Naming accuracy by majority vote: 1 sighting 85%, 3 → 96%, 5 → 99% (optimistic: assumes independent errors).

### 1c. Detector: is an AI model running here?
Small AI model (Qwen 1.5B) vs ordinary heavy jobs, on GitHub machines.

| Test | AI caught | False alarms on unseen ordinary jobs |
|---|---|---|
| A. On the computer (process signals) | 1 of 2 AI setups (server 100%, benchmark 0%) | 0% |
| B. Model split across 2 machines (network only) | 100% (same setup, new run) | 75% |

→ A relies on one signal: a big model file loaded into memory. That's easy to hide, and the disguised-AI run didn't produce data. B flags almost any unfamiliar traffic. **The detector does not work yet.**

## 2. Epidemic model for a rogue self-copying AI
100k cheap devices, 50 internet providers, 90 days; all numbers assumed.
No defence: peak 92,195 infected; half that by day 24.

| Detection delay | All providers act | 95% | 80% | 50% |
|---|---|---|---|---|
| 1 hour | 0% still spreading | 8% | 23% | 52% |
| 3 days | 0% | 10% | 33% | 88% |
| 1 week | 0% | 40% | 98% | 100% |

| Single lever (bad case: 80% cooperate, 1-week delay) | Still spreading | Infected left |
|---|---|---|
| Nothing extra | 98% | 3,679 |
| Patch half the TV boxes beforehand | 86% | 596 |
| Faster owner patching | 81% | 74 |
| Network filtering only | 100% | 35,055 |

→ Clear thresholds: holdout providers matter more than speed once a few % refuse. The cheapest, most numerous devices are the biggest lever. Filtering alone fails.

## 3. Time–space: open-model family trees (Hugging Face)
493 base models from 24 labs; derivatives (fine-tunes, quantisations, adapters) over time.

| Predictors of size at day 180 | Rank correlation | Top-10 caught | Typical error |
|---|---|---|---|
| Count at day 14 | 0.76 | 5/10 | 2.2× |
| + speed, breadth, type mix | 0.77 | 5/10 | 2.1× |

→ Very predictable, but the obvious signal does all the work. Extra signals add almost nothing.

## 4. Humanoid robot leagues (RoboCup)
280 matches, each predicted only from earlier games.

| League | Games predicted | Accuracy | When rating gap > 150 |
|---|---|---|---|
| HSL 2026 | 102 | 67% | 78% (9 games) |
| SPL 2004–2025 | 74 | 84% | 100% (29 games) |

→ Predictable, but data is tiny and one team (B-Human) dominates.

## 5. Sperm migration map (VISEM-Tracking)
20 men, 920 sperm tracked for at least 1 second, compared with each man's lab tests.

| Lab result | Best path feature | Correlation | p (adjusted for 8 tries) | Leave-one-man-out |
|---|---|---|---|---|
| Progressive motility (sanity check) | share fast & straight | +0.64 | 0.03 | +0.45 |
| Immotile (sanity check) | share barely moving | +0.72 | 0.01 | +0.41 |
| **DNA fragmentation (new)** | median speed | **−0.48** | 0.29 | −0.19 |
| Normal shape | median speed | +0.40 | 0.72 | fails |

→ The tracks are good (they recover the lab's motility). The new signal is that slower swimmers go with more DNA damage. It's only a hint: not significant with 20 men.

## 6. Wastewater → hospital admissions (CDC, all US states)
Trained up to Jul 2025, tested on the 16 months after.

| Disease (1 week ahead) | Error, admissions only | + own sewage | + neighbours' sewage | Rise/fall called right |
|---|---|---|---|---|
| COVID | 0.288 | 0.284 | 0.278 (−3%) | 55% → 61% |
| Flu A | 0.388 | 0.382 | 0.376 (−3%) | 51% → 60% |
| RSV | 0.387 | 0.386 | 0.386 (0%) | 52% → 54% |

At 2 weeks ahead: COVID −5%, flu −4%. → Real but small gain. CDC already works in this space.

## 7. Children's chest X-rays with little data
5,232 child X-rays (pneumonia vs normal); test set 624. AUC: 0.5 = coin flip, 1.0 = perfect.

| Child X-rays per class | General image model | Adult chest X-ray model | Gain |
|---|---|---|---|
| 5 | 0.835 | **0.920** | +0.085 |
| 25 | 0.883 | 0.931 | +0.048 |
| 100 | 0.917 | 0.950 | +0.033 |
| all 5,232 | 0.953 | 0.964 | +0.011 |

Adult model with no child training at all: 0.583. → With only 10 child X-rays, a model built on adult X-rays is about as good as a general model trained on 200. Strongest clean result.

## 8. What changed since your last scan (NIH repeat X-rays)
25,000 X-rays, 6,585 patients, 18,414 before/after pairs; 34% show a new finding.

| Model sees | AUC for "new finding today" |
|---|---|
| Today's scan only | 0.640 |
| Today + previous scan + difference | 0.621 |
| Difference only | 0.540 |

→ Negative: the previous scan did not help. The labels are text-mined and noisy. A proper test needs radiologist-labelled change data (MIMIC, credentialed).

## Ranking

| Rank | Idea | Result strength | Novelty | Best use |
|---|---|---|---|---|
| 1 | Children's X-rays with little data | Strong, clean | Medium (transfer learning is known) | Paper with a paediatric radiologist; tool for hospitals with few child scans |
| 2 | Sperm paths → DNA damage | Weak but promising hint | High (we found no one linking swim paths to DFI) | Paper with an IVF clinic; needs about 100+ men |
| 3 | Rogue-AI epidemic model | Clear, useful thresholds | Medium–high | AI-safety grant or policy paper, not a product |
| 4 | Fingerprinting agents | Strong (85%) | Low (model attribution is studied) | Feature inside a security product |
| 5 | Open-model spread | Strong but obvious | Low | Analytics feature only |
| 6 | Wastewater nowcast | Small gain | Low (CDC) | Skip |
| 7 | Humanoid leagues | Good, tiny data | Low market | Skip |
| 8 | AI detector | Fails | – | Skip unless redesigned |
| 9 | Change since last scan | Negative | – | Retry only with MIMIC |
