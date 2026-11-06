# AI-agent early warning: lures, fingerprints and containment

Research code for a project that **catches AI agents doing harm, names the model behind them, and works out how to
contain a self-copying AI**. Everything runs on GitHub Actions; results are committed to `results/`.
Older, unrelated experiments are preserved on the branch `archive-2026-11-06`.

Ethics: every test is passive or sandboxed. No live systems are attacked, bait only ever pays out dust, the
"malware" in `pilots/aimalware` is a harmless imitation talking to a mock AI server, and nothing "hacks back".

## Pieces and pilots

| Piece | Folder | What it tests | Headline result |
|---|---|---|---|
| A. Containment | `pilots/epidemic` | Where a self-copying AI lives (home devices, PCs, cloud, web2/web3 GPU) and which shields stop it; v4 calibrated with real Mirai clean-up data | Survivors retreat to cloud + web3 GPU; it dies only if accounts are closed faster than it can open them |
| B. Lures | `pilots/lures`, `pilots/huntsim`, `pilots/sensors` | Do AI models take AI-targeted bait? How do they look for targets? How fast do strategies catch careful agents? | Bait picked 49–100% vs 5–18% for ordinary results; 10,000 smart lures catch searching agents in hours vs 100,000 random decoys in ~8 days |
| B. On-chain bait | `pilots/chainbait` | Do AI agents pick bait contracts? Local-chain detection demo | Bait contracts picked 69–100% vs 5–10% ordinary; attackers flagged in the same block, 0 false alarms |
| B. Worm tripwires | `pilots/tripwire` | Do AI email assistants obey and pass on a harmless tripwire (Morris II-style worm detection)? | running |
| C. Fingerprints | `pilots/fingerprint` | Naming the model from commands (86%), website behaviour (67%), tool calls (30%) | see results/fingerprint |
| C. Modified models | `pilots/retrained` | Do bait and fingerprint survive safety-removed ("abliterated") models? | Bait works as well or better; family still recognisable |
| Device shield | `pilots/detector`, `pilots/aimalware` | Spotting AI programs on a machine; spotting malware that calls AI services (PROMPTFLUX-like) | Detector weak so far; AI-malware refined rule flags the imitation, not legit coding agents |

Summary of all numbers: `pilots/AGENT-SECURITY-RESULTS-2026-11-06.md`.
