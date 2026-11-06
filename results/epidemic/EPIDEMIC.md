# Epidemic model for a self-replicating AI on cheap devices

100,000 vulnerable devices across 50 internet providers; worm needs 15 TV-box-equivalents of computing power before it can spread; 60-80 simulated outbreaks per setting (same random worlds for every option, so rows are directly comparable), 90 days each. All numbers are assumptions.

**No defence:** peak 92,195 infected devices; half of that reached by day 24.

## 1. How fast must providers act, and how many must cooperate?

Cells: chance the worm is STILL ABLE TO SPREAD at day 90 · infected devices left at day 90 (median). (Below 15 TV-box-equivalents the leftover infected devices cannot act.)

| Detection delay | 100% of providers | 99% | 95% | 80% | 50% |
|---|---|---|---|---|---|
| 1 h | 0% · 0 | 0% · 0 | 8% · 0 | 23% · 0 | 52% · 11,178 |
| 6 h | 0% · 0 | 2% · 0 | 3% · 0 | 23% · 0 | 45% · 2 |
| 24 h | 0% · 0 | 0% · 0 | 7% · 0 | 25% · 2 | 45% · 6 |
| 72 h | 0% · 0 | 2% · 0 | 10% · 0 | 33% · 6 | 88% · 44,466 |
| 168 h | 0% · 0 | 8% · 0 | 40% · 8 | 98% · 3,679 | 100% · 48,180 |

## 2. Which devices matter most? (patch 50% of one device class before the outbreak; bad-case world: 80% of providers cooperate, 1-week detection)

| Patched class | Still spreading at day 90 | Peak infected | Left at day 90 |
|---|---|---|---|
| none | 98% | 3,679 | 3,679 |
| TV box (70,000 devices) | 86% | 596 | 596 |
| router (20,000 devices) | 96% | 2,483 | 2,483 |
| NAS (8,000 devices) | 89% | 2,684 | 2,684 |
| gaming PC / GPU box (2,000 devices) | 92% | 1,880 | 1,880 |

## 3. Which response matters most? (same bad-case world: 80% cooperate, 1-week detection)

| Response | Still spreading at day 90 | Peak | Left at day 90 |
|---|---|---|---|
| Clean 50% of infected per hour + filter 90% of incoming (baseline) | 98% | 3,679 | 3,679 |
| Clean only (no filtering) | 96% | 5,256 | 5,256 |
| Filter only (no cleaning) | 100% | 35,055 | 35,055 |
| Slow cleaning (10%/hour) | 99% | 3,763 | 3,763 |
| Faster owner patching (2%/day instead of 0.2%) | 81% | 202 | 74 |
