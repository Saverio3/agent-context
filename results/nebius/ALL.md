# nebius: all methods, sorted by net saving (★ = best trade-off: nothing saves more at equal or lower risk)

| | Method | Saved (conversation) | Net after fetch-back | Miss rate |
|---|---|---|---|---|
|  | CEILING: perfect foresight (not buildable) | 71.2% | 71.2% | 0.0% |
| ★ | Tree memory (fractal idea, offline proxy) | 69.7% | 68.2% | 3.5% |
|  | Tree + echo, only last step in full (new) | 71.2% | 67.5% | 6.5% |
|  | Full stack (collapse + echo + old agent notes shortened) | 68.0% | 66.7% | 3.6% |
| ★ | Tree + echo + cap long fresh outputs (new) | 67.5% | 66.2% | 3.1% |
| ★ | R2 Slow decay (new) | 67.4% | 66.1% | 3.1% |
|  | Tree + echo (new) | 67.2% | 65.9% | 3.1% |
| ★ | R4 Sticky unfold (new) | 66.8% | 65.6% | 3.1% |
| ★ | R1 Working set (new) | 66.2% | 65.0% | 3.0% |
| ★ | R6 Lean guards (new) | 65.6% | 64.4% | 2.9% |
| ★ | Curve: frame + hide old outputs after 2 steps | 60.2% | 59.7% | 1.1% |
|  | Curve: JetBrains masking, keep last 2 | 60.1% | 59.6% | 1.1% |
|  | Version collapse + masking | 58.5% | 58.0% | 1.2% |
|  | R3 Keep the agent's notes (new) | 58.0% | 57.5% | 1.3% |
|  | Echo retention + drop unechoed outputs | 57.2% | 56.7% | 1.3% |
| ★ | Ants: pheromone trails | 56.6% | 56.2% | 0.7% |
|  | Echo retention (new) | 56.5% | 56.0% | 1.3% |
|  | Curve: JetBrains masking, keep last 3 | 56.3% | 56.0% | 0.7% |
| ★ | Brain: 7 chunks (Miller) | 56.2% | 55.9% | 0.7% |
| ★ | Ours: ensemble vote | 55.4% | 55.1% | 0.7% |
|  | Data eng: LSM-tree tiers | 55.4% | 55.1% | 0.7% |
|  | Elephant: landmark locations | 55.2% | 54.9% | 0.7% |
|  | R5 All guards combined (new) | 55.3% | 54.8% | 1.2% |
|  | Space: store-and-forward priority | 55.0% | 54.7% | 0.7% |
|  | Brain: predictive coding | 54.9% | 54.5% | 0.7% |
| ★ | Curve: frame + hide old outputs after 5 steps | 54.4% | 54.1% | 0.4% |
|  | Low-pass memory (epicycloid idea) | 54.6% | 54.1% | 1.2% |
|  | Brain: sleep consolidation | 54.3% | 54.0% | 0.7% |
|  | Elephant matriarch: goal anchoring | 54.1% | 53.7% | 0.7% |
|  | Ours: spreading activation | 53.6% | 53.2% | 0.7% |
|  | Medicine: SOAP vital findings | 53.4% | 53.0% | 0.7% |
|  | Medicine: ESI triage | 53.3% | 53.0% | 0.7% |
|  | Brain: place cells / cognitive map | 53.2% | 52.9% | 0.6% |
|  | Memory palace (method of loci) | 52.8% | 52.5% | 0.7% |
|  | Tree + cap + safety net (new) | 53.2% | 52.1% | 2.5% |
|  | Data eng: delta-encoded file views | 52.3% | 52.1% | 0.6% |
|  | Learned keep/hide, 3% miss target (new) | 51.8% | 51.4% | 1.0% |
|  | Brain: event segmentation | 50.8% | 50.6% | 0.6% |
| ★ | Brain: sparse coding | 50.5% | 50.3% | 0.4% |
|  | Radiology: windowing around hits | 50.4% | 50.1% | 0.5% |
|  | Brain: amygdala surprise tagging | 50.1% | 49.8% | 0.4% |
|  | Learned keep/hide, 1% miss target (new) | 50.0% | 49.6% | 1.0% |
|  | Observation masking (JetBrains 2025) | 49.7% | 49.5% | 0.4% |
|  | Brain: synaptic tag and capture | 49.0% | 48.9% | 0.4% |
| ★ | Control: feedback controller | 49.0% | 48.8% | 0.3% |
| ★ | Curve: frame + hide old outputs after 10 steps | 48.4% | 48.3% | 0.2% |
|  | Medicine: drug half-life per kind | 47.7% | 47.6% | 0.2% |
|  | Computing: knapsack value density | 46.0% | 45.8% | 0.3% |
|  | Brain: hippocampal replay | 45.9% | 45.8% | 0.4% |
| ★ | Stats: exponential forgetting | 45.0% | 44.9% | 0.2% |
|  | Brain: reconsolidation | 45.0% | 44.9% | 0.3% |
|  | Version collapse | 45.2% | 44.8% | 0.9% |
|  | Stats: Beta-Binomial need estimate | 44.5% | 44.4% | 0.3% |
|  | Space: progressive transmission | 44.4% | 44.2% | 0.3% |
|  | Computing: ARC cache | 43.1% | 43.0% | 0.2% |
|  | Brain: Ebbinghaus spaced repetition | 42.7% | 42.7% | 0.2% |
| ★ | Curve: frame + hide old outputs after 20 steps | 42.0% | 42.0% | 0.1% |
|  | Curve: JetBrains masking, keep last 10 | 36.6% | 36.5% | 0.2% |
| ★ | Curve: JetBrains masking, keep last 20 | 20.5% | 20.4% | 0.0% |
| ★ | Baseline (re-read everything) | 0.0% | 0.0% | 0.0% |
