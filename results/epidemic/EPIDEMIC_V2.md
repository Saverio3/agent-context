# Where would a self-copying AI live, and which shield stops it? (model v2)

Three habitats: home devices, cloud accounts, rented GPUs on decentralised markets; model files on undeletable storage allow restarts. 60 simulated outbreaks per row, 90 days, detection delay 3 days. 'Still alive' = still has enough computing power to act at day 90. Compute in TV-box units.

| Shields on | Still alive at day 90 | Peak compute | Compute at day 90 |
|---|---|---|---|
| none | 100% | 531,352 | 480,759 |
| Device shield | 100% | 526,044 | 483,974 |
| ISP cleaning | 100% | 186,260 | 184,340 |
| Cloud watch | 100% | 516,241 | 463,393 |
| Market checks | 100% | 469,308 | 418,140 |
| Storage takedown | 100% | 531,352 | 480,759 |
| Device shield + ISP cleaning | 100% | 186,360 | 184,545 |
| ISP cleaning + Cloud watch | 100% | 146,403 | 142,475 |
| Cloud watch + Market checks | 100% | 451,398 | 397,456 |
| ISP cleaning + Cloud watch + Market checks | 88% | 9,508 | 6,720 |
| Device shield + ISP cleaning + Cloud watch + Market checks | 40% | 682 | 0 |
| ISP cleaning + Cloud watch + Market checks + Storage takedown | 83% | 10,044 | 6,485 |
| Device shield + ISP cleaning + Cloud watch + Market checks + Storage takedown | 27% | 705 | 0 |

## Leave-one-out: all shields on except one

| Missing shield | Still alive at day 90 |
|---|---|
| Device shield | 83% |
| ISP cleaning | 100% |
| Cloud watch | 98% |
| Market checks | 100% |
| Storage takedown | 40% |
