# Agent context lab — swegym public agent runs - group bc - test half, runs the predictor never saw

Runs: 1554 · model calls: 27666 · median calls per run: 14 · baseline tokens re-read: 325,664,973

What gets re-read: tool 84% · assistant 9% · task 7% · system 1%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 61.4% | 66.2% | 64.8% | 3.3% |
| R3 Keep the agent's notes (new) | no | 75.0% | 80.9% | 78.2% | 6.5% |
| Brain: Ebbinghaus spaced repetition | no | 43.1% | 46.5% | 45.9% | 1.6% |
| Ants: pheromone trails | no | 68.7% | 74.0% | 72.3% | 4.2% |
| Brain: place cells / cognitive map | no | 66.8% | 72.0% | 70.3% | 3.9% |
| Brain: event segmentation | no | 57.5% | 62.0% | 60.7% | 3.0% |
| Brain: amygdala surprise tagging | no | 58.0% | 62.5% | 61.2% | 2.3% |
| Brain: predictive coding | no | 66.5% | 71.7% | 70.1% | 3.8% |
| Memory palace (method of loci) | no | 63.0% | 67.9% | 66.3% | 3.9% |
| Elephant matriarch: goal anchoring | no | 65.1% | 70.1% | 68.5% | 3.9% |
| Brain: hippocampal replay | no | 51.6% | 55.7% | 54.8% | 2.3% |
| Brain: sleep consolidation | no | 66.1% | 71.2% | 69.6% | 3.9% |
| Brain: synaptic tag and capture | no | 56.7% | 61.1% | 60.0% | 2.7% |
| Brain: 7 chunks (Miller) | no | 67.5% | 72.8% | 71.1% | 4.0% |
| Brain: reconsolidation | no | 48.4% | 52.2% | 51.5% | 1.9% |
| Elephant: landmark locations | no | 66.8% | 72.0% | 70.3% | 3.9% |
| Brain: sparse coding | no | 54.9% | 59.2% | 58.4% | 1.9% |
| Medicine: ESI triage | no | 58.8% | 63.4% | 61.9% | 3.5% |
| Medicine: SOAP vital findings | no | 63.5% | 68.5% | 67.0% | 3.6% |
| Medicine: drug half-life per kind | no | 47.7% | 51.5% | 50.7% | 1.7% |

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
