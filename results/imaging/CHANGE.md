# What changed since your last scan? (NIH ChestX-ray14 repeat scans)

24,999 X-rays from 6,585 patients → 18,414 consecutive pairs; 34% of pairs show a finding the previous scan didn't have. 5-fold split by patient. Labels are text-mined from reports (noisy), so absolute AUCs are capped.

| What the model sees | AUC for 'new finding today' |
|---|---|
| Today's scan alone | 0.640 |
| Today + previous scan + difference | 0.621 |
| Difference only | 0.540 |

Most common new findings: Infiltration (2086), Atelectasis (1259), Effusion (1233), Nodule (621), Consolidation (609), Pneumothorax (466)
