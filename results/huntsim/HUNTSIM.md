# Catching a careful AI agent: strategies compared (same 1,000-item budget)

Median days until 5 sightings over 400 simulated agents (capped at 1,095 days = 3 years). Lure pick rates used: average lure 63%, best lure for that model 88%, ordinary result 11% (measured in the lure pilot). Effort: 1,000 probes/hour or 20 target searches/day.

| Defender strategy | random scanner | habitat forager | searcher | searcher + trails |
|---|---|---|---|---|
| scatter | 744 days | 701 days | never (3y+) | never (3y+) |
| habitat decoys | 721 days | 16 days | never (3y+) | never (3y+) |
| search lures | never (3y+) | never (3y+) | 46 h | 45 h |
| lures + trails | never (3y+) | never (3y+) | 45 h | 22 h |
| + tailored | never (3y+) | never (3y+) | 38 h | 18 h |
| portfolio | never (3y+) | 32 days | 3 days | 38 h |

Reference from the earlier decoy maths: random-scan decoys need 100,000 to see a 1,000-probes/hour agent 5 times in ~8 days.

Key assumptions: cloud/GPU ranges = 2% of address space; foragers put 90% of probes there; 20 target searches/day; 1,000 lures make a lure appear in 20% of relevant searches; trails followed with prob 0.6 per hop.
