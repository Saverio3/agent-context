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
