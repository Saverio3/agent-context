# Open-model family trees: does week 1–2 predict day 180?

Base models: 493 from 24 organisations, released 2022-03-02 – 2026-05-04. Median derivatives by day 180: 16 (max 15,831; 0 hit the 20k download cap, counted as 20k). Cross-validation grouped by organisation.

| Predictors | Rank correlation with day-180 size | Top-10 caught | Typical error (×) |
|---|---|---|---|
| day-14 count only | 0.76 | 5/10 | 2.21× |
| + day-7 count (speed) | 0.77 | 4/10 | 2.19× |
| + distinct authors (breadth) | 0.77 | 4/10 | 2.16× |
| + type mix (quant / fine-tune / adapter / merge) | 0.77 | 5/10 | 2.09× |

Holding the day-14 count fixed, breadth (authors per derivative) vs later growth: rank correlation +0.13.

## Biggest trees

| Base model | Released | Day 14 | Authors day 14 | Day 180 |
|---|---|---|---|---|
| black-forest-labs/FLUX.1-dev | 2024-07-31 | 85 | 64 | 15,831 |
| stabilityai/stable-diffusion-xl-base-1.0 | 2023-07-25 | 47 | 26 | 2,489 |
| Qwen/Qwen3.6-27B | 2026-04-21 | 349 | 195 | 1,751 |
| Qwen/Qwen3.5-9B | 2026-02-27 | 151 | 99 | 1,695 |
| Qwen/Qwen3.6-35B-A3B | 2026-04-15 | 303 | 195 | 1,598 |
| meta-llama/Llama-3.1-8B-Instruct | 2024-07-18 | 130 | 91 | 1,491 |
| Qwen/Qwen3.5-4B | 2026-02-27 | 141 | 99 | 1,454 |
| mistralai/Mistral-7B-v0.1 | 2023-09-20 | 13 | 10 | 1,217 |
| meta-llama/Meta-Llama-3-8B-Instruct | 2024-04-17 | 167 | 89 | 1,203 |
| mistralai/Mistral-7B-Instruct-v0.2 | 2023-12-11 | 42 | 25 | 1,059 |
| google/gemma-4-E4B-it | 2026-03-02 | 1 | 1 | 994 |
| meta-llama/Meta-Llama-3-8B | 2024-04-17 | 183 | 89 | 992 |
