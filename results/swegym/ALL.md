# swegym: all methods, sorted by net saving (★ = best trade-off: nothing saves more at equal or lower risk)

| | Method | Saved (conversation) | Net after fetch-back | Miss rate |
|---|---|---|---|---|
|  | CEILING: perfect foresight (not buildable) | 93.1% | 93.1% | 0.0% |
| ★ | Tree + echo, only last step in full (new) | 87.9% | 83.7% | 25.7% |
| ★ | Tree + echo + cap long fresh outputs (new) | 86.1% | 82.4% | 16.8% |
| ★ | R2 Slow decay (new) | 86.0% | 82.3% | 16.7% |
| ★ | R4 Sticky unfold (new) | 85.9% | 82.2% | 16.7% |
| ★ | R1 Working set (new) | 85.0% | 81.4% | 16.3% |
| ★ | R6 Lean guards (new) | 84.8% | 81.2% | 16.2% |
|  | Tree memory (fractal idea, offline proxy) | 83.0% | 79.6% | 16.4% |
| ★ | R3 Keep the agent's notes (new) | 80.9% | 78.2% | 6.5% |
|  | Tree + cap + safety net (new) | 81.2% | 78.0% | 14.1% |
|  | Tree + echo (new) | 80.8% | 77.8% | 15.1% |
| ★ | Curve: JetBrains masking, keep last 2 | 79.6% | 77.4% | 5.5% |
| ★ | Curve: frame + hide old outputs after 2 steps | 79.5% | 77.3% | 5.4% |
|  | Full stack (collapse + echo + old agent notes shortened) | 79.3% | 76.5% | 14.6% |
|  | R5 All guards combined (new) | 78.4% | 75.9% | 5.9% |
| ★ | Curve: JetBrains masking, keep last 3 | 75.0% | 73.2% | 4.5% |
|  | Echo retention + drop unechoed outputs | 74.5% | 72.6% | 4.8% |
|  | Echo retention (new) | 74.2% | 72.4% | 4.7% |
| ★ | Ants: pheromone trails | 74.0% | 72.3% | 4.2% |
| ★ | Brain: 7 chunks (Miller) | 72.8% | 71.1% | 4.0% |
|  | Version collapse + masking | 72.8% | 71.0% | 4.4% |
|  | Low-pass memory (epicycloid idea) | 72.5% | 70.7% | 4.3% |
| ★ | Ours: ensemble vote | 72.3% | 70.7% | 3.9% |
|  | Data eng: LSM-tree tiers | 72.1% | 70.5% | 3.9% |
|  | Brain: place cells / cognitive map | 72.0% | 70.3% | 3.9% |
|  | Elephant: landmark locations | 72.0% | 70.3% | 3.9% |
| ★ | Brain: predictive coding | 71.7% | 70.1% | 3.8% |
|  | Brain: sleep consolidation | 71.2% | 69.6% | 3.9% |
|  | Space: store-and-forward priority | 70.8% | 69.2% | 3.8% |
|  | Elephant matriarch: goal anchoring | 70.1% | 68.5% | 3.9% |
| ★ | Ours: spreading activation | 70.0% | 68.5% | 3.8% |
| ★ | Medicine: SOAP vital findings | 68.5% | 67.0% | 3.6% |
|  | Memory palace (method of loci) | 67.9% | 66.3% | 3.9% |
| ★ | Data eng: delta-encoded file views | 67.0% | 65.6% | 2.8% |
|  | Radiology: windowing around hits | 66.9% | 65.5% | 3.0% |
| ★ | Computing: knapsack value density | 66.9% | 65.5% | 2.7% |
|  | Curve: frame + hide old outputs after 5 steps | 66.7% | 65.3% | 3.3% |
|  | Observation masking (JetBrains 2025) | 66.2% | 64.8% | 3.3% |
|  | Medicine: ESI triage | 63.4% | 61.9% | 3.5% |
|  | Control: feedback controller | 63.1% | 61.9% | 2.8% |
| ★ | Brain: amygdala surprise tagging | 62.5% | 61.2% | 2.3% |
| ★ | Space: progressive transmission | 62.2% | 61.1% | 2.2% |
|  | Brain: event segmentation | 62.0% | 60.7% | 3.0% |
|  | Brain: synaptic tag and capture | 61.1% | 60.0% | 2.7% |
| ★ | Brain: sparse coding | 59.2% | 58.4% | 1.9% |
|  | Learned keep/hide, 3% miss target (new) | 56.5% | 55.4% | 2.8% |
|  | Brain: hippocampal replay | 55.7% | 54.8% | 2.3% |
|  | Learned keep/hide, 1% miss target (new) | 54.5% | 53.5% | 2.6% |
|  | Stats: Beta-Binomial need estimate | 52.4% | 51.6% | 2.1% |
|  | Brain: reconsolidation | 52.2% | 51.5% | 1.9% |
| ★ | Medicine: drug half-life per kind | 51.5% | 50.7% | 1.7% |
| ★ | Stats: exponential forgetting | 49.9% | 49.3% | 1.6% |
|  | Curve: frame + hide old outputs after 10 steps | 49.2% | 48.5% | 1.7% |
|  | Computing: ARC cache | 48.5% | 47.9% | 1.8% |
|  | Curve: JetBrains masking, keep last 10 | 46.9% | 46.2% | 1.7% |
|  | Brain: Ebbinghaus spaced repetition | 46.5% | 45.9% | 1.6% |
|  | Version collapse | 36.8% | 35.9% | 2.6% |
| ★ | Curve: frame + hide old outputs after 20 steps | 26.6% | 26.4% | 0.5% |
| ★ | Curve: JetBrains masking, keep last 20 | 21.3% | 21.0% | 0.5% |
| ★ | Baseline (re-read everything) | 0.0% | 0.0% | 0.0% |
