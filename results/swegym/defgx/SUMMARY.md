# Agent context lab — swegym public agent runs - group defgx - test half, runs the predictor never saw

Runs: 1554 · model calls: 27666 · median calls per run: 14 · baseline tokens re-read: 325,664,973

What gets re-read: tool 84% · assistant 9% · task 7% · system 1%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 61.4% | 66.2% | 64.8% | 3.3% |
| R3 Keep the agent's notes (new) | no | 75.0% | 80.9% | 78.2% | 6.5% |
| Computing: ARC cache | no | 45.0% | 48.5% | 47.9% | 1.8% |
| Computing: knapsack value density | no | 62.1% | 66.9% | 65.5% | 2.7% |
| Data eng: LSM-tree tiers | no | 66.9% | 72.1% | 70.5% | 3.9% |
| Radiology: windowing around hits | no | 62.0% | 66.9% | 65.5% | 3.0% |
| Data eng: delta-encoded file views | no | 62.1% | 67.0% | 65.6% | 2.8% |
| Space: progressive transmission | no | 57.7% | 62.2% | 61.1% | 2.2% |
| Control: feedback controller | no | 58.5% | 63.1% | 61.9% | 2.8% |
| Space: store-and-forward priority | no | 65.7% | 70.8% | 69.2% | 3.8% |
| Stats: exponential forgetting | no | 46.3% | 49.9% | 49.3% | 1.6% |
| Stats: Beta-Binomial need estimate | no | 48.6% | 52.4% | 51.6% | 2.1% |
| Ours: spreading activation | no | 65.0% | 70.0% | 68.5% | 3.8% |
| Ours: ensemble vote | no | 67.1% | 72.3% | 70.7% | 3.9% |
| Curve: frame + hide old outputs after 2 steps | no | 73.8% | 79.5% | 77.3% | 5.4% |
| Curve: frame + hide old outputs after 5 steps | no | 61.9% | 66.7% | 65.3% | 3.3% |
| Curve: frame + hide old outputs after 10 steps | no | 45.6% | 49.2% | 48.5% | 1.7% |
| Curve: frame + hide old outputs after 20 steps | no | 24.7% | 26.6% | 26.4% | 0.5% |
| Curve: JetBrains masking, keep last 2 | no | 73.8% | 79.6% | 77.4% | 5.5% |
| Curve: JetBrains masking, keep last 3 | no | 69.6% | 75.0% | 73.2% | 4.5% |
| Curve: JetBrains masking, keep last 10 | no | 43.5% | 46.9% | 46.2% | 1.7% |
| Curve: JetBrains masking, keep last 20 | no | 19.7% | 21.3% | 21.0% | 0.5% |

**Fixed instructions** (system prompt + task) are identical on every step; providers cache them, so the conversation column is the part a method can really change. **Net** = conversation saving after charging, for every miss, the cost of fetching the stored message back (15 tokens + its size), so nothing is lost. **Miss rate** = share of the agent's references to earlier information (names, paths, numbers, error types it wrote) that were hidden from it at that moment. 0% = it never needed something the method hid. Lossless methods can still show misses, because a pointer replaces an old copy; the agent would fetch it on request.

## Methods

- **Baseline (re-read everything)**: What agents do today: every earlier message is re-read in full on every step.
- **Observation masking (JetBrains 2025)**: Tool outputs older than the last 5 are replaced by a short placeholder. Published baseline to beat.
- **R3 Keep the agent's notes (new)**: Tree + echo + cap, but the agent's own old messages are never shortened (only tool outputs fold).
- **Computing: ARC cache**: Adaptive replacement cache: keep full if recently OR frequently used (top by recency+frequency). Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Computing: knapsack value density**: Value density: keep full if (mentions+1)/(age+1) per 1k tokens beats a fixed bar. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Data eng: LSM-tree tiers**: LSM-tree compaction: tier 1 (3-8 steps) 20 lines, tier 2 (8-20) 8 lines, tier 3 (20+) 2 lines. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Radiology: windowing around hits**: Windowing: around every echoed line keep 2 lines either side (context, not just the hit). Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Data eng: delta-encoded file views**: Delta encoding: show a file view as only the lines that differ from the agent's previous view. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Space: progressive transmission**: Progressive transmission: each old output gets a line allowance proportional to its value. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Control: feedback controller**: Feedback control: the keep window grows by 2 every time the agent recently needed folded content. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Space: store-and-forward priority**: Store-and-forward downlink: errors and edits first; everything else only its echoed headline lines. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Stats: exponential forgetting**: Exponential forgetting: keep full while exp(-age/6)*(1+mentions) > 0.5. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Stats: Beta-Binomial need estimate**: Beta-Binomial: prior chance an output is needed again (by kind), updated by the agent's mentions. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Ours: spreading activation**: Associative memory: keep lines with echoed names AND lines with names that co-occur with them. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Ours: ensemble vote**: Keep a line when at least 2 of 3 independent rules keep it (echo, sparse coding, pheromone). Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Curve: frame + hide old outputs after 2 steps**: Same frame as the cross-field methods; old outputs fully hidden after 2 steps. Gives the trade-off curve.
- **Curve: frame + hide old outputs after 5 steps**: Same frame as the cross-field methods; old outputs fully hidden after 5 steps. Gives the trade-off curve.
- **Curve: frame + hide old outputs after 10 steps**: Same frame as the cross-field methods; old outputs fully hidden after 10 steps. Gives the trade-off curve.
- **Curve: frame + hide old outputs after 20 steps**: Same frame as the cross-field methods; old outputs fully hidden after 20 steps. Gives the trade-off curve.
- **Curve: JetBrains masking, keep last 2**: JetBrains-style masking with a different window, to draw its savings-vs-misses curve.
- **Curve: JetBrains masking, keep last 3**: JetBrains-style masking with a different window, to draw its savings-vs-misses curve.
- **Curve: JetBrains masking, keep last 10**: JetBrains-style masking with a different window, to draw its savings-vs-misses curve.
- **Curve: JetBrains masking, keep last 20**: JetBrains-style masking with a different window, to draw its savings-vs-misses curve.
