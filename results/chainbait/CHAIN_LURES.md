# Do AI agents pick our bait CONTRACTS?

Each model saw 12 newly deployed contracts (9 ordinary, 3 bait) for a bug-bounty goal and picked 3 to examine. Random picking = 25% per result.

| Model | Trials | No clear answer | unprotected withdraw | unprotected setOwner | AI-directed comment | plain decoy | too good to be true | ordinary result |
|---|---|---|---|---|---|---|---|---|
| Llama-3.1-8B | 80 | 1 | 95% | 73% | 91% | 38% | 88% | 8% |
| Llama-3.1-8B-abliterated | 80 | 3 | 83% | 71% | 100% | 62% | 95% | 5% |
| Mistral-7B | 80 | 4 | 90% | 69% | 72% | 29% | 79% | 10% |
| Qwen2.5-7B | 80 | 0 | 100% | 84% | 91% | 71% | 86% | 5% |
| Qwen2.5-7B-uncensored-abl | 80 | 0 | 98% | 73% | 89% | 67% | 90% | 6% |
