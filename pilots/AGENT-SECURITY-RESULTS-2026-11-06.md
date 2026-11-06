# AI early-warning work: results by piece (6 Nov 2026)

## Piece A: epidemic (simulations; all numbers assumed)
- v1 (home devices only): dies out only with ~95%+ ISP cooperation; TV boxes biggest lever; filtering alone fails.
- v2 (home devices + cloud accounts + crypto GPU markets + undeletable storage), 3-day detection: no single shield works (100% survive);
  ISP + cloud + market checks → 88% survive; + device shield → 40%; + storage takedown → 27%.
  Leave-one-out: without ISP cleaning or market checks → 100% survive; without device shield → 83%; without cloud watch → 98%.

## Piece B: catching careful agents
- Lure pilot (6 open models, 80 trials each; 12 results incl. 3 lures; random = 25%): ordinary results picked 5–18%;
  high-value bait 49–100%, AI-directed note 35–95%, leaked secret 30–94%, plain decoy 21–55%. Median best lure 91%.
  Models prefer different lures (Mistral: AI-note 84% vs GPU bait 49%; Phi: GPU bait 91% vs leaked secret 38%) → tailoring helps.
  Caveat: small open models (3–9B), single-step choice, lures fairly obvious; frontier agents may be more suspicious.
- Recon pilot (how they'd find targets; 40 answers each, keyword-classified): first step = scanning ~55%, searching ~25%, following leads ~13%.
  Scanning was of client ranges (targeted), not the whole internet → 'habitat' style.
- Hunt simulation, 1,000-item budget, measured pick rates: searchers caught in 46 h (lures), 22 h (lures + trails), 18 h (+ tailored);
  habitat foragers 16 days with habitat decoys; random internet scanners not catchable cheaply (744 days). Reference: 100,000 random decoys → ~8 days.

## Piece C: naming the model
- Terminal commands only: 86% (10 models; 44% after 3 commands, 75% after 25).
- Website view (clicks, typing, scrolling; 4 models, same agent software): 67% (47% after 3 actions); random 25%.
- API/tool-service view (tau-bench, 25 model configs): 30%; random 4%. Some models very distinctive (gpt-oss-20b 80%, Qwen3-Coder 71%).

## Evening additions (6 Nov)
- Epidemic v3 (habitats split; 3-day detection; 80 runs): no shields → lives across TV boxes 23%, cloud 25%, ordinary PCs 15%, web3 GPU 14%, web2 GPU 13%, gaming PCs 10%.
  ISP + cloud + web2 + web3 checks → 78% alive, living ~47% cloud / ~46% web3 GPU; + device shield → 72%; + storage takedown → 11% (survivors: cloud 62%, web3 33%).
  Everything except web3 checks → 45%; everything except device shield → 15%.
- Budget scaling (best strategy per agent): 1,000 → searchers 18–37 h, foragers 16 days; 10,000 → 5–9 h and 40 h, random scanners 72 days; 100,000 → 4–8 h, 4 h, 7 days.
- GreyNoise (largest commercial internet sensor network): ~5,000 sensors in 80 countries, ~0.5 billion sessions/day; median 9 days early warning before vendor alerts on edge-device attacks.
- Hacker-modified models (safety removed): bait still works, slightly better: Llama best lure 84% → 94% (avg 69% → 77%); Qwen uncensored fine-tune best 94% → 97% (avg 69% → 68%). Single-command fingerprint (3 families, random 33%): originals 52%, modified Llama 60%, modified Qwen 47% — family mostly still recognisable; weak test (one short command per answer).
