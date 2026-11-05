# Agent context lab — nebius public agent runs

Runs: 2987 · model calls: 75324 · median calls per run: 16 · baseline tokens re-read: 839,570,772

What gets re-read: tool 57% · assistant 23% · system 11% · task 9%

| Method | Lossless | Tokens saved (all) | Saved on the conversation (excl. fixed instructions) | Median per run | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0.0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 40.4% | 50.6% | 16.7% | 0.4% |
| Version collapse | yes | 38.3% | 47.9% | 23.1% | 0.8% |
| Version collapse + masking | no | 47.6% | 59.6% | 29.9% | 1.0% |
| Low-pass memory (epicycloid idea) | no | 44.8% | 56.1% | 29.2% | 1.0% |
| Tree memory (fractal idea, offline proxy) | no | 55.8% | 69.9% | 35.9% | 3.1% |
| Echo retention (new) | no | 46.2% | 57.9% | 30.4% | 1.1% |
| Echo retention + drop unechoed outputs | no | 46.7% | 58.5% | 30.7% | 1.1% |
| Full stack (collapse + echo + old agent notes shortened) | no | 55.2% | 69.2% | 34.5% | 3.2% |
| CEILING: perfect foresight (not buildable) | no | 56.9% | 71.3% | 48.1% | 0.0% |

**Fixed instructions** (system prompt + task) are identical on every step; providers cache them, so the conversation column is the part a method can really change. **Miss rate** = share of the agent's references to earlier information (names, paths, numbers, error types it wrote) that were hidden from it at that moment. 0% = it never needed something the method hid. Lossless methods can still show misses, because a pointer replaces an old copy; the agent would fetch it on request.

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
