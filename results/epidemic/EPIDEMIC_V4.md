# Rogue-AI epidemic, recalibrated with real-world numbers (model v4)

ISP cleanup from the Mirai field study (walled garden: 92% cleaned in 14 days; 5% re-infection); speeds bracketed by Mirai's 76-minute doubling. Cloud/GPU-market numbers still assumed. 60 outbreaks per cell, 90 days.

## A. All shields on: % still alive at day 90

| Spread speed | Detected in 1 day | 3 days | 7 days | 14 days |
|---|---|---|---|---|
| Mirai-fast (76-min doubling) | 100% | 100% | 100% | 100% |
| Medium (6 h) | 100% | 100% | 100% | 100% |
| Slow (60 h) | 42% | 70% | 93% | 98% |

## B. Which shields matter (medium speed, 3-day detection)

| Shields | Still alive | TV boxes & small devices | Gaming PCs | PCs & laptops | Big cloud | Web2 GPU | Web3 GPU |
|---|---|---|---|---|---|---|---|
| None | 100% | 4% | 2% | 3% | 45% | 21% | 26% |
| ISP walled garden only | 100% | 0% | 0% | 0% | 50% | 22% | 28% |
| ISP + cloud + web2 + web3 checks | 100% | 0% | 0% | 0% | 62% | 4% | 34% |
| + device shield | 100% | 0% | 0% | 0% | 62% | 4% | 34% |
| Everything | 100% | 0% | 0% | 0% | 62% | 4% | 34% |
| Everything except web3 checks | 100% | 0% | 0% | 0% | 43% | 3% | 53% |
| Everything except device shield | 100% | 0% | 0% | 0% | 62% | 4% | 34% |
| Everything except ISP | 100% | 17% | 0% | 0% | 51% | 4% | 29% |
| Everything except storage takedown | 100% | 0% | 0% | 0% | 62% | 4% | 34% |

## C. Cloud takedown speed (everything on, medium speed, 3-day detection)

| Cloud closes accounts in | Still alive |
|---|---|
| 0.5 days | 7% |
| 2 days | 100% |
| 7 days | 100% |

## D. How easily it opens new cloud / GPU accounts (everything on, medium speed, 3-day detection, cloud 2 days)

| Account-opening rate vs baseline | Still alive |
|---|---|
| 0.05x | 0% |
| 0.1x | 0% |
| 0.3x | 0% |
| 1x | 100% |
