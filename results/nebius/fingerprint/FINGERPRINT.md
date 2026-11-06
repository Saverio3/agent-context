# Fingerprinting pilot — 11910 runs, 3 models (≥60 runs each)

Train 8045 runs / test 3865 runs on tasks the detector never saw.

| Model | Runs |
|---|---|
| swe-agent-llama-70b | 11233 |
| swe-agent-llama-8b | 514 |
| swe-agent-llama-405b | 163 |

## A. Identify the exact model (3 classes)

- Accuracy on unseen tasks: **93.4%** (top-2: 98.2%)
- Always guessing the most common class: 93.4%

| Model | Recognised correctly |
|---|---|
| swe-agent-llama-70b | 100% |
| swe-agent-llama-405b | 0% |
| swe-agent-llama-8b | 0% |

## B. Predict the agent's next command

- Generic predictor (all models pooled): **26.3%** of next commands right
- Knowing which model it is: **26.0%**
- 432,087 predictions on unseen tasks. Upper bound for B: assumes the model was identified correctly.
