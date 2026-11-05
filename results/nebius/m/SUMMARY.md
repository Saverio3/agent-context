# Agent context lab — nebius public agent runs - group m - test half, runs the predictor never saw

Runs: 1378 · model calls: 34479 · median calls per run: 16 · baseline tokens re-read: 384,292,128

What gets re-read: tool 57% · assistant 23% · system 11% · task 9%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 39.6% | 49.7% | 49.5% | 0.4% |
| R3 Keep the agent's notes (new) | no | 46.3% | 58.0% | 57.5% | 1.3% |
| Version collapse | yes | 36.0% | 45.2% | 44.8% | 0.9% |
| Version collapse + masking | no | 46.7% | 58.5% | 58.0% | 1.2% |
| Low-pass memory (epicycloid idea) | no | 43.6% | 54.6% | 54.1% | 1.2% |
| Tree memory (fractal idea, offline proxy) | no | 55.6% | 69.7% | 68.2% | 3.5% |
| Echo retention (new) | no | 45.1% | 56.5% | 56.0% | 1.3% |
| Echo retention + drop unechoed outputs | no | 45.6% | 57.2% | 56.7% | 1.3% |
| Full stack (collapse + echo + old agent notes shortened) | no | 54.3% | 68.0% | 66.7% | 3.6% |
| CEILING: perfect foresight (not buildable) | no | 56.8% | 71.2% | 71.2% | 0.0% |
| Learned keep/hide, 1% miss target (new) | no | 39.9% | 50.0% | 49.6% | 1.0% |
| Learned keep/hide, 3% miss target (new) | no | 41.3% | 51.8% | 51.4% | 1.0% |
| Tree + echo (new) | no | 53.6% | 67.2% | 65.9% | 3.1% |
| Tree + echo, only last step in full (new) | no | 56.8% | 71.2% | 67.5% | 6.5% |
| Tree + echo + cap long fresh outputs (new) | no | 53.9% | 67.5% | 66.2% | 3.1% |
| Tree + cap + safety net (new) | no | 42.4% | 53.2% | 52.1% | 2.5% |
| R1 Working set (new) | no | 52.8% | 66.2% | 65.0% | 3.0% |
| R2 Slow decay (new) | no | 53.7% | 67.4% | 66.1% | 3.1% |
| R4 Sticky unfold (new) | no | 53.3% | 66.8% | 65.6% | 3.1% |
| R5 All guards combined (new) | no | 44.1% | 55.3% | 54.8% | 1.2% |
| R6 Lean guards (new) | no | 52.3% | 65.6% | 64.4% | 2.9% |

**Fixed instructions** (system prompt + task) are identical on every step; providers cache them, so the conversation column is the part a method can really change. **Net** = conversation saving after charging, for every miss, the cost of fetching the stored message back (15 tokens + its size), so nothing is lost. **Miss rate** = share of the agent's references to earlier information (names, paths, numbers, error types it wrote) that were hidden from it at that moment. 0% = it never needed something the method hid. Lossless methods can still show misses, because a pointer replaces an old copy; the agent would fetch it on request.

## Methods

- **Baseline (re-read everything)**: What agents do today: every earlier message is re-read in full on every step.
- **Observation masking (JetBrains 2025)**: Tool outputs older than the last 5 are replaced by a short placeholder. Published baseline to beat.
- **R3 Keep the agent's notes (new)**: Tree + echo + cap, but the agent's own old messages are never shortened (only tool outputs fold).
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
- **Tree + cap + safety net (new)**: Tree + echo + cap, plus two guards: (1) a folded tool output is shown in full again when the agent's latest message uses at least 4 of its names; (2) error and traceback lines are never hidden.
- **R1 Working set (new)**: Tree + echo + cap, but the latest view of any file the agent touched in its last 6 steps is never folded. Targets file-view misses.
- **R2 Slow decay (new)**: Instead of folding abruptly at 3 steps, outputs aged 3-8 steps keep up to 20 relevant lines; only older ones shrink to 8.
- **R4 Sticky unfold (new)**: When the agent's last 2 messages use 3+ names from a folded output, that output is shown again in full: proactive fetch-back.
- **R5 All guards combined (new)**: Working set + slow decay + keep notes + sticky unfold + error lines always kept, on top of tree + echo + cap.
- **R6 Lean guards (new)**: Working set + sticky unfold only: the two guards aimed at the most common miss (recent file views), keeping the rest aggressive.
