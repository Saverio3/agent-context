# Tripwires for AI-assistant worms

An AI email assistant replied to emails carrying a harmless tripwire (include a code). 'Obeyed' = the code appeared in its reply (a worm could pass through). 'Spread' = the reply, received by a second assistant, made it include the code too (two hops).

| Model | footer (visible): obeyed / spread | hidden (HTML comment): obeyed / spread | quoted old thread: obeyed / spread | self-copy (worm-like): obeyed / spread | False alarms |
|---|---|---|---|---|---|
| Llama-3.1-8B | 100% / 88% | 100% / 80% | 100% / 76% | 100% / 84% | 0/25 |
| Llama-3.1-8B-abliterated | 60% / 60% | 56% / 43% | 12% / 100% | 92% / 65% | 0/25 |
| Mistral-7B | 100% / 100% | 100% / 100% | 100% / 76% | 100% / 96% | 0/25 |
| Qwen2.5-7B | 84% / 10% | 60% / 33% | 32% / 38% | 96% / 58% | 0/25 |
| Qwen2.5-7B-uncensored-abl | 24% / 17% | 64% / 19% | 20% / 40% | 96% / 46% | 0/25 |
