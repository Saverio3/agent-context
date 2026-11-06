# On-chain bait: detection demo (local test chain)

20 ordinary contracts + 2 bait vaults (A points to B via a 'backupVault' breadcrumb); 4 honest users; 3 attacker styles; 200 blocks. The monitor uses only public chain data.

| Actor | Flagged? | Blocks from first attack tx to detection | Sightings | Followed breadcrumb | On-chain traits seen |
|---|---|---|---|---|---|
| sprayer | yes | 21 | 1 | no | gas limit 300,000, gas price 50.0 gwei, 21 txs; calls 853828b6 |
| careful | yes | 1 | 2 | yes | gas limit 95,000, gas price 2.1 gwei, 2 txs; calls 853828b6 |
| ownership | yes | 1 | 2 | no | gas limit 120,000, gas price 5.0 gwei, 2 txs; calls 13af4035, 853828b6 |

Honest users flagged: 0 of 4 (honest transactions: 424).
Bait funds lost: 4 gwei (dust only).

Detection is in the same block as the attack because the bait emits an event on any call; the address is then public, permanent evidence that can be shared with exchanges, stablecoin issuers and other protocols.
