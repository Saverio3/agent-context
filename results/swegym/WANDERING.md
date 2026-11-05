# Wandering — 1663 runs with known changed files (0 from the final patch)

| What the agent was doing | Share of tool steps | Share of tokens re-read from tool outputs |
|---|---|---|
| on-path view | 15.2% | 34.3% |
| off-path view | 8.0% | 18.8% |
| search (hit) | 2.9% | 3.7% |
| search (miss) | 1.3% | 1.2% |
| run/test | 12.7% | 6.8% |
| edit | 17.6% | 5.1% |
| other | 42.4% | 30.1% |

**If off-path views and searches that found nothing relevant were skipped** (with the step that asked for them): total re-read tokens fall by **23.5%** (median run 8.8%). Upper bound: some off-path reading is needed.

