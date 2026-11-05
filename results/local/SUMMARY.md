# Agent context lab — data/local

Runs: 22 · model calls: 230 · median calls per run: 11 · baseline tokens re-read: 1,074,294

What gets re-read: tool 40% · task 25% · system 25% · assistant 10%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Net, after fetching back what was missed | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 11.0% | 22.1% | 21.8% | 0.3% |
| Version collapse | yes | 9.5% | 19.0% | 19.0% | 0.0% |
| Version collapse + masking | no | 19.1% | 38.3% | 38.1% | 0.3% |
| Low-pass memory (epicycloid idea) | no | 18.2% | 36.5% | 36.2% | 0.2% |
| Tree memory (fractal idea, offline proxy) | no | 25.5% | 51.1% | 50.3% | 1.2% |
| Echo retention (new) | no | 19.3% | 38.7% | 38.4% | 0.3% |
| Echo retention + drop unechoed outputs | no | 19.4% | 38.8% | 38.5% | 0.3% |
| Full stack (collapse + echo + old agent notes shortened) | no | 21.4% | 42.9% | 42.5% | 1.2% |
| CEILING: perfect foresight (not buildable) | no | 43.8% | 87.7% | 87.7% | 0.0% |
| Learned keep/hide, 1% miss target (new) | no | 9.5% | 19.0% | 19.0% | 0.0% |
| Learned keep/hide, 3% miss target (new) | no | 9.5% | 19.0% | 19.0% | 0.0% |
| Tree + echo (new) | no | 23.0% | 46.0% | 45.6% | 1.0% |
| Tree + echo, only last step in full (new) | no | 30.1% | 60.3% | 59.3% | 4.5% |
| Tree + echo + cap long fresh outputs (new) | no | 24.6% | 49.2% | 46.5% | 2.1% |
| Tree + cap + safety net (new) | no | 22.8% | 45.6% | 43.0% | 2.1% |
| R1 Working set (new) | no | 23.2% | 46.4% | 43.7% | 2.1% |
| R2 Slow decay (new) | no | 24.2% | 48.5% | 45.8% | 2.1% |
| R3 Keep the agent's notes (new) | no | 22.6% | 45.2% | 42.6% | 1.6% |
| R4 Sticky unfold (new) | no | 23.7% | 47.5% | 44.8% | 2.1% |
| R5 All guards combined (new) | no | 20.0% | 40.1% | 37.5% | 1.6% |
| R6 Lean guards (new) | no | 22.4% | 44.8% | 42.1% | 2.1% |

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
- **Tree + cap + safety net (new)**: Tree + echo + cap, plus two guards: (1) a folded tool output is shown in full again when the agent's latest message uses at least 4 of its names; (2) error and traceback lines are never hidden.
- **R1 Working set (new)**: Tree + echo + cap, but the latest view of any file the agent touched in its last 6 steps is never folded. Targets file-view misses.
- **R2 Slow decay (new)**: Instead of folding abruptly at 3 steps, outputs aged 3-8 steps keep up to 20 relevant lines; only older ones shrink to 8.
- **R3 Keep the agent's notes (new)**: Tree + echo + cap, but the agent's own old messages are never shortened (only tool outputs fold).
- **R4 Sticky unfold (new)**: When the agent's last 2 messages use 3+ names from a folded output, that output is shown again in full: proactive fetch-back.
- **R5 All guards combined (new)**: Working set + slow decay + keep notes + sticky unfold + error lines always kept, on top of tree + echo + cap.
- **R6 Lean guards (new)**: Working set + sticky unfold only: the two guards aimed at the most common miss (recent file views), keeping the rest aggressive.
