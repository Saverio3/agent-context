# Agent context lab — swegym public agent runs - test half, runs the predictor never saw

Runs: 1554 · model calls: 27666 · median calls per run: 14 · baseline tokens re-read: 325,664,973

What gets re-read: tool 84% · assistant 9% · task 7% · system 1%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 61.4% | 66.2% | 64.8% | 3.3% |
| Version collapse | yes | 34.1% | 36.8% | 35.9% | 2.6% |
| Version collapse + masking | no | 67.5% | 72.8% | 71.0% | 4.4% |
| Low-pass memory (epicycloid idea) | no | 67.2% | 72.5% | 70.7% | 4.3% |
| Tree memory (fractal idea, offline proxy) | no | 77.0% | 83.0% | 79.6% | 16.4% |
| Echo retention (new) | no | 68.8% | 74.2% | 72.4% | 4.7% |
| Echo retention + drop unechoed outputs | no | 69.1% | 74.5% | 72.6% | 4.8% |
| Full stack (collapse + echo + old agent notes shortened) | no | 73.5% | 79.3% | 76.5% | 14.6% |
| CEILING: perfect foresight (not buildable) | no | 86.3% | 93.1% | 93.1% | 0.0% |
| Learned keep/hide, 1% miss target (new) | no | 50.6% | 54.5% | 53.5% | 2.6% |
| Learned keep/hide, 3% miss target (new) | no | 52.4% | 56.5% | 55.4% | 2.8% |
| Tree + echo (new) | no | 74.9% | 80.8% | 77.8% | 15.1% |
| Tree + echo, only last step in full (new) | no | 81.5% | 87.9% | 83.7% | 25.7% |
| Tree + echo + cap long fresh outputs (new) | no | 79.9% | 86.1% | 82.4% | 16.8% |

**Fixed instructions** (system prompt + task) are identical on every step; providers cache them, so the conversation column is the part a method can really change. **Net** = conversation saving after charging, for every miss, the cost of fetching the stored message back (15 tokens + its size), so nothing is lost. **Miss rate** = share of the agent's references to earlier information (names, paths, numbers, error types it wrote) that were hidden from it at that moment. 0% = it never needed something the method hid. Lossless methods can still show misses, because a pointer replaces an old copy; the agent would fetch it on request.

## Methods

- **Baseline (re-read everything)**: What agents do today: every earlier message is re-read in full on every step.
- **Observation masking (JetBrains 2025)**: Tool outputs older than the last 5 are replaced by a short placeholder. Published baseline to beat.
- **Version collapse**: An older view of a file the agent later re-opened, or an exact repeat of an earlier output, becomes a pointer. Only superseded copies are hidden; the latest copy is always visible.
- **Version collapse + masking**: Both of the above together.
- **Low-pass memory (epicycloid idea)**: Slow layer kept in full: task, instructions, every agent message (its plans and decisions). Fast layer squeezed, not hidden: tool outputs older than the last 3 keep only their first and last 6 lines. Built on version collapse.
- **Tree memory (fractal idea, offline proxy)**: Recent 3 steps are leaves in full. Older steps fold into a branch line each: the agent's own first sentence for that step plus the first line of its output; full leaves stay in storage. A real version would use an AI to write branch summaries; this proxy needs no AI.
- **Echo retention (new)**: Uses the agent's own words as the relevance signal. In tool outputs older than the last 3, keep only lines containing something the agent or the task has already mentioned (names, paths, numbers, error types), plus the first 2 lines. Everything else is stored, not shown. No AI call; decided from the past only.
- **Echo retention + drop unechoed outputs**: Echo retention, and old outputs with zero echoed lines become a pointer entirely.
- **Full stack (collapse + echo + old agent notes shortened)**: Version collapse and echo retention, plus the agent's own messages older than the last 3 steps are cut to their first 2 sentences (its decisions, not its long reasoning). Everything stored.
- **CEILING: perfect foresight (not buildable)**: Upper bound, for reference only. Instructions and task kept; from every other earlier message keep only the lines whose names/paths/numbers the agent will actually use later. Shows the most any method could save.
- **Learned keep/hide, 1% miss target (new)**: Version collapse, then each line of a tool output, once it is 3 steps old, is scored by a model trained on other runs: 'will the agent need this later?'. Lines below a threshold set for a 1% miss target are stored, not shown. Error/pass lines are always kept.
- **Learned keep/hide, 3% miss target (new)**: Version collapse, then each line of a tool output, once it is 3 steps old, is scored by a model trained on other runs: 'will the agent need this later?'. Lines below a threshold set for a 3% miss target are stored, not shown. Error/pass lines are always kept.
- **Tree + echo (new)**: Tree memory, but each folded old output keeps its first line plus up to 8 lines mentioning things the agent or task already named, instead of one line only. Aims at tree-level savings with fewer misses.
- **Tree + echo, only last step in full (new)**: Same as Tree + echo, but only the most recent step stays in full (more aggressive).
- **Tree + echo + cap long fresh outputs (new)**: Tree + echo, and even recent outputs longer than 120 lines show only the first 60 and last 40 lines (the rest stored). Targets huge logs and file dumps that dominate OpenHands runs.
