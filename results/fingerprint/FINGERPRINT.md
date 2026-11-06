# Fingerprinting pilot — 19860 runs, 3 models (≥60 runs each)

Train/test split by task: the same task never appears in both.

## A. Which model is it?

| Evidence seen | Accuracy |
|---|---|
| Guessing the most common model (baseline) | 94.7% |
| First 3 steps only | 53.3% |
| First 25% of the run | 64.0% |
| First half of the run | 72.1% |
| Whole run | 76.0% |

| Model | Test runs | Correctly identified |
|---|---|---|
| swe-agent-llama-70b | 5456 | 79% |
| swe-agent-llama-8b | 284 | 26% |
| swe-agent-llama-405b | 87 | 23% |

Strongest giveaways per model (top 6 habits):

- **swe-agent-llama-405b**: o_the_`get`, o_the_`schema`, o_the_`field_singleton_schema`, o_the_`marshmallow`, o_the_`pyproject.toml`, o_the_`to_camel`
- **swe-agent-llama-70b**: n_2, o_the_`reproduce_bug.py`, n_3, b_edit_open, n_4, o_the_`core.py`
- **swe-agent-llama-8b**: o_the_`_minhash_encoder.py`, o_the_`resumableupload`, o_the_`picklecache.py`, o_the_necessary, o_the_`graph.py`, o_the_`minhashencoder`

## B. Can we predict its next move? (second half of each test run)

| Predictor | Next command type correct |
|---|---|
| Generic (all models pooled) | 59.8% |
| Specialised to the model the fingerprint guessed | 58.8% |
| Specialised to the true model (upper bound) | 59.6% |

Predictions scored: 77,832. Command types: 886 distinct.
