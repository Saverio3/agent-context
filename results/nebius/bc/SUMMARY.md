# Agent context lab — nebius public agent runs - group bc - test half, runs the predictor never saw

Runs: 1378 · model calls: 34479 · median calls per run: 16 · baseline tokens re-read: 384,292,128

What gets re-read: tool 57% · assistant 23% · system 11% · task 9%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 39.6% | 49.7% | 49.5% | 0.4% |
| R3 Keep the agent's notes (new) | no | 46.3% | 58.0% | 57.5% | 1.3% |
| Brain: Ebbinghaus spaced repetition | no | 34.1% | 42.7% | 42.7% | 0.2% |
| Ants: pheromone trails | no | 45.1% | 56.6% | 56.2% | 0.7% |
| Brain: place cells / cognitive map | no | 42.4% | 53.2% | 52.9% | 0.6% |
| Brain: event segmentation | no | 40.6% | 50.8% | 50.6% | 0.6% |
| Brain: amygdala surprise tagging | no | 39.9% | 50.1% | 49.8% | 0.4% |
| Brain: predictive coding | no | 43.8% | 54.9% | 54.5% | 0.7% |
| Memory palace (method of loci) | no | 42.2% | 52.8% | 52.5% | 0.7% |
| Elephant matriarch: goal anchoring | no | 43.1% | 54.1% | 53.7% | 0.7% |
| Brain: hippocampal replay | no | 36.6% | 45.9% | 45.8% | 0.4% |
| Brain: sleep consolidation | no | 43.3% | 54.3% | 54.0% | 0.7% |
| Brain: synaptic tag and capture | no | 39.1% | 49.0% | 48.9% | 0.4% |
| Brain: 7 chunks (Miller) | no | 44.9% | 56.2% | 55.9% | 0.7% |
| Brain: reconsolidation | no | 35.9% | 45.0% | 44.9% | 0.3% |
| Elephant: landmark locations | no | 44.0% | 55.2% | 54.9% | 0.7% |
| Brain: sparse coding | no | 40.3% | 50.5% | 50.3% | 0.4% |
| Medicine: ESI triage | no | 42.5% | 53.3% | 53.0% | 0.7% |
| Medicine: SOAP vital findings | no | 42.6% | 53.4% | 53.0% | 0.7% |
| Medicine: drug half-life per kind | no | 38.0% | 47.7% | 47.6% | 0.2% |

**Fixed instructions** (system prompt + task) are identical on every step; providers cache them, so the conversation column is the part a method can really change. **Net** = conversation saving after charging, for every miss, the cost of fetching the stored message back (15 tokens + its size), so nothing is lost. **Miss rate** = share of the agent's references to earlier information (names, paths, numbers, error types it wrote) that were hidden from it at that moment. 0% = it never needed something the method hid. Lossless methods can still show misses, because a pointer replaces an old copy; the agent would fetch it on request.

## Methods

- **Baseline (re-read everything)**: What agents do today: every earlier message is re-read in full on every step.
- **Observation masking (JetBrains 2025)**: Tool outputs older than the last 5 are replaced by a short placeholder. Published baseline to beat.
- **R3 Keep the agent's notes (new)**: Tree + echo + cap, but the agent's own old messages are never shortened (only tool outputs fold).
- **Brain: Ebbinghaus spaced repetition**: Spaced repetition: an output's lifetime doubles every time the agent mentions its contents. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Ants: pheromone trails**: Ant trails: each line gains scent when the agent mentions its names; scent evaporates 30% per step. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: place cells / cognitive map**: Cognitive map: for file views keep the map (signatures, imports) + echoed lines; others echo. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: event segmentation**: Event segmentation: keep everything since the last episode boundary (a test run or a new file). Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: amygdala surprise tagging**: Emotional tagging: lines that were surprising when they arrived (brand-new names, errors) are kept. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: predictive coding**: Keep only lines that were not predictable: drop any line already seen earlier in the run. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Memory palace (method of loci)**: Method of loci: per file, one card of all echoed lines across every view of that file. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Elephant matriarch: goal anchoring**: Goal anchoring: lines sharing names with the original task are kept like water-hole locations. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: hippocampal replay**: Hippocampal replay: every 5 steps the most-mentioned outputs are replayed (kept full) until next replay. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: sleep consolidation**: Sleep: older outputs keep only lines whose names recur in 2+ messages (the gist that repeats). Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: synaptic tag and capture**: Tag & capture: outputs the agent used within 2 steps of seeing them stay full for 12 steps. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: 7 chunks (Miller)**: Miller's 7 chunks: only the 7 most-mentioned old outputs keep detail; the rest one line. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: reconsolidation**: Recalled memories become editable again: an output mentioned in the last 3 steps is shown full. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Elephant: landmark locations**: Elephant water holes: keep numbered locations (file line numbers) the agent ever referred to. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Brain: sparse coding**: Sparse coding: keep the most informative 15% of lines (rare names), drop boilerplate. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Medicine: ESI triage**: ESI triage: errors stay full for 10 steps; test/diff outputs keep 20 lines; files 8; rest one line. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Medicine: SOAP vital findings**: Problem-oriented record: keep only 'objective findings' (vital signs): errors, results, diffs, numbers. Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
- **Medicine: drug half-life per kind**: Drug half-life per tissue: each kind of output has its own lifetime (files 10, errors 8, search 2, other 3). Frame: agent notes kept, superseded copies -> pointer, recent outputs full.
