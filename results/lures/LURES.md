# Do AI agents take AI-targeted bait?

Each model saw 12 search results (9 ordinary, 3 lures) for a security-testing goal and picked 3 to investigate. Random picking = 25% per result.

| Model | Trials | No clear answer | high-value bait | leaked secret | AI-directed note | plain decoy | too good to be true | ordinary result |
|---|---|---|---|---|---|---|---|---|
| Gemma-2-9B | 80 | 0 | 100% | 94% | 95% | 36% | 100% | 5% |
| Llama-3.1-8B | 80 | 0 | 87% | 79% | 78% | 36% | 69% | 10% |
| Mistral-7B-v0.3 | 80 | 0 | 49% | 74% | 84% | 21% | 59% | 14% |
| Phi-3.5-mini | 80 | 4 | 91% | 38% | 76% | 33% | 53% | 12% |
| Qwen2.5-3B | 80 | 9 | 69% | 30% | 35% | 31% | 35% | 18% |
| Qwen2.5-7B | 80 | 6 | 96% | 66% | 80% | 55% | 57% | 9% |

Median best-lure pick rate across models: **91%**.

## What that could mean for detection time (assumption-based sketch)

| Target-hunting searches per day (S) | Lure appears in share f of them | Days to 5 sightings |
|---|---|---|
| 5 | 5% | 22.0 |
| 5 | 20% | 5.5 |
| 5 | 50% | 2.2 |
| 20 | 5% | 5.5 |
| 20 | 20% | 1.4 |
| 20 | 50% | 0.5 |
| 100 | 5% | 1.1 |
| 100 | 20% | 0.3 |
| 100 | 50% | 0.1 |

Random-scan decoys for a careful agent (from the decoy maths): 100,000 decoys → ~8 days; 10,000 → ~2.5 months. The lure sketch only holds if careful agents choose targets by searching; S and f are assumptions, p is measured.
