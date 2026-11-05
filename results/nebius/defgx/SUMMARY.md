# Agent context lab — nebius public agent runs - group defgx - test half, runs the predictor never saw

Runs: 1378 · model calls: 34479 · median calls per run: 16 · baseline tokens re-read: 384,292,128

What gets re-read: tool 57% · assistant 23% · system 11% · task 9%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 39.6% | 49.7% | 49.5% | 0.4% |
| R3 Keep the agent's notes (new) | no | 46.3% | 58.0% | 57.5% | 1.3% |
| Computing: ARC cache | no | 34.4% | 43.1% | 43.0% | 0.2% |
| Computing: knapsack value density | no | 36.7% | 46.0% | 45.8% | 0.3% |
| Data eng: LSM-tree tiers | no | 44.2% | 55.4% | 55.1% | 0.7% |
| Radiology: windowing around hits | no | 40.2% | 50.4% | 50.1% | 0.5% |
| Data eng: delta-encoded file views | no | 41.8% | 52.3% | 52.1% | 0.6% |
| Space: progressive transmission | no | 35.4% | 44.4% | 44.2% | 0.3% |
| Control: feedback controller | no | 39.1% | 49.0% | 48.8% | 0.3% |
| Space: store-and-forward priority | no | 43.9% | 55.0% | 54.7% | 0.7% |
| Stats: exponential forgetting | no | 35.9% | 45.0% | 44.9% | 0.2% |
| Stats: Beta-Binomial need estimate | no | 35.5% | 44.5% | 44.4% | 0.3% |
| Ours: spreading activation | no | 42.7% | 53.6% | 53.2% | 0.7% |
| Ours: ensemble vote | no | 44.2% | 55.4% | 55.1% | 0.7% |
| Curve: frame + hide old outputs after 2 steps | no | 48.0% | 60.2% | 59.7% | 1.1% |
| Curve: frame + hide old outputs after 5 steps | no | 43.4% | 54.4% | 54.1% | 0.4% |
| Curve: frame + hide old outputs after 10 steps | no | 38.6% | 48.4% | 48.3% | 0.2% |
| Curve: frame + hide old outputs after 20 steps | no | 33.5% | 42.0% | 42.0% | 0.1% |
| Curve: JetBrains masking, keep last 2 | no | 47.9% | 60.1% | 59.6% | 1.1% |
| Curve: JetBrains masking, keep last 3 | no | 44.9% | 56.3% | 56.0% | 0.7% |
| Curve: JetBrains masking, keep last 10 | no | 29.2% | 36.6% | 36.5% | 0.2% |
| Curve: JetBrains masking, keep last 20 | no | 16.3% | 20.5% | 20.4% | 0.0% |

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
