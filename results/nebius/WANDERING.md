# Wandering — 2688 runs with known changed files (2688 from the final patch)

| What the agent was doing | Share of tool steps | Share of tokens re-read from tool outputs |
|---|---|---|
| on-path view | 22.2% | 36.0% |
| off-path view | 12.1% | 20.3% |
| search (hit) | 9.9% | 4.0% |
| search (miss) | 5.2% | 1.8% |
| run/test | 11.9% | 8.2% |
| edit | 19.1% | 23.9% |
| other | 19.5% | 5.9% |

**If off-path views and searches that found nothing relevant were skipped** (with the step that asked for them): total re-read tokens fall by **23.0%** (median run 8.6%). Upper bound: some off-path reading is needed.

- Solved runs: 648, median wandering saving 7.6%
- Unsolved runs: 2040, median wandering saving 9.1%
