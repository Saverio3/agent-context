# agent-context lab

Coding agents re-read their whole history before every step. This lab tests ways to make them re-read less,
on real public agent runs, with the same scores for every method and failures kept in the table.

- `lab/methods/` — one file per method (add a file to add a method)
- `lab/core.py` — replay + scoring (tokens re-read, miss rate)
- `lab/fetch_data.py` — downloads public runs from Hugging Face (runs on GitHub Actions)
- `results/` — written automatically; `results/local/` = 22 small sample runs in `data/local/`

Run locally: `python -m lab.run --local data/local --out results/local`

Scores: **tokens saved** vs re-reading everything; **miss rate** = share of the agent's references to earlier
facts (names, paths, numbers, error types) that the method had hidden at that moment. Tokens ≈ characters / 4.
