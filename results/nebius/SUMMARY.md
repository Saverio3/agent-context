# Agent context lab — nebius public agent runs

Runs: 2987 · model calls: 75324 · median calls per run: 16 · baseline tokens re-read: 839,570,772

| Method | Lossless | Tokens saved (all runs) | Median saving per run | Runs saving ≥30% | Miss rate |
|---|---|---|---|---|---|
| Baseline (re-read everything) | yes | 0.0% | 0.0% | 0% | 0.0% |
| Observation masking (JetBrains 2025) | no | 40.4% | 16.7% | 35% | 0.4% |
| Version collapse | yes | 38.3% | 23.1% | 38% | 0.8% |
| Version collapse + masking | no | 47.6% | 29.9% | 50% | 1.0% |
| Low-pass memory (epicycloid idea) | no | 44.8% | 29.2% | 49% | 1.0% |
| Tree memory (fractal idea, offline proxy) | no | 55.8% | 35.9% | 58% | 3.1% |
| Echo retention (new) | no | 46.2% | 30.4% | 51% | 1.1% |
| Echo retention + drop unechoed outputs | no | 46.7% | 30.7% | 51% | 1.1% |

**Miss rate** = share of the agent's references to earlier information (names, paths, numbers, error types it wrote) that were hidden from it at that moment. 0% = it never needed something the method hid. Lossless methods can still show misses, because a pointer replaces an old copy; the agent would fetch it on request.

## Methods

- **Baseline (re-read everything)**: What agents do today: every earlier message is re-read in full on every step.
- **Observation masking (JetBrains 2025)**: Tool outputs older than the last 5 are replaced by a short placeholder. Published baseline to beat.
- **Version collapse**: An older view of a file the agent later re-opened, or an exact repeat of an earlier output, becomes a pointer. Only superseded copies are hidden; the latest copy is always visible.
- **Version collapse + masking**: Both of the above together.
- **Low-pass memory (epicycloid idea)**: Slow layer kept in full: task, instructions, every agent message (its plans and decisions). Fast layer squeezed, not hidden: tool outputs older than the last 3 keep only their first and last 6 lines. Built on version collapse.
- **Tree memory (fractal idea, offline proxy)**: Recent 3 steps are leaves in full. Older steps fold into a branch line each: the agent's own first sentence for that step plus the first line of its output; full leaves stay in storage. A real version would use an AI to write branch summaries; this proxy needs no AI.
- **Echo retention (new)**: Uses the agent's own words as the relevance signal. In tool outputs older than the last 3, keep only lines containing something the agent or the task has already mentioned (names, paths, numbers, error types), plus the first 2 lines. Everything else is stored, not shown. No AI call; decided from the past only.
- **Echo retention + drop unechoed outputs**: Echo retention, and old outputs with zero echoed lines become a pointer entirely.
