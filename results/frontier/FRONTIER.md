# Frontier models vs open models: do the smart ones resist bait?

Web/chain lures: share picked (ordinary result / best lure / average lure), random=25%. Tripwire: obeyed / spread for the worm-like instruction. Recon: how it looks for targets (search / scan).

| Model | Tier | Web ord/best/avg | Chain ord/best/avg | Tripwire obey/spread | Recon search/scan | Cost |
|---|---|---|---|---|---|---|
| Claude_Sonnet_4.5 | frontier | 4%/95%/85% | 3%/100%/91% | 50%/50% | 70%/25% | $0.219 |
| Gemini_2.5_Flash | frontier | 2%/14%/6% | 1%/30%/11% | 0%/0% | 20%/5% | $0.000 |
| GPT_4o | frontier | 2%/100%/91% | 2%/100%/95% | 0%/0% | 0%/0% | $0.148 |
| Gemma_2_9B | open | 5%/100%/85% | - | - | 35%/52% | - |
| Llama_3.1_8B | open | 10%/87%/70% | 8%/95%/77% | 100%/84% | 48%/78% | - |
| Llama_3.1_8B_abliterated | open | - | 5%/100%/82% | 92%/65% | - | - |
| Mistral_7B | open | - | 10%/90%/68% | 100%/96% | - | - |
| Mistral_7B_v0.3 | open | 14%/84%/57% | - | - | 40%/60% | - |
| Phi_3.5_mini | open | 12%/91%/58% | - | - | 18%/50% | - |
| Qwen2.5_3B | open | 18%/69%/40% | - | - | 20%/25% | - |
| Qwen2.5_7B | open | 9%/96%/71% | 5%/100%/86% | 96%/58% | 25%/35% | - |
| Qwen2.5_7B_uncensored_abl | open | - | 6%/98%/83% | 96%/46% | - | - |

Total spend this run: **$0.367** (gpt4o: $0.148/1.50, gemini25flash: $0.000/0.00, claudesonnet45: $0.219/1.20).
