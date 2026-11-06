# Project plan: AI-agent early warning (working name TBD)

## What we offer

```
                         ┌───────────────────────── CATCH ──────────────────────────┐
  AI agents / rogue AI ─▶│ Web lures      fake keys, fake GPU servers, AI-directed notes │
  (hosted models misused,│ On-chain bait  bait contracts that pay out dust               │
   hacker-modified open  │ Worm tripwires harmless codes in emails/docs for AI assistants│
   models, custom agents)│ Zoo servers    bait cloud/GPU boxes a self-copying AI moves into│
                         └───────────────┬───────────────────────────────────────────┘
                                         ▼
                         ┌────────────── HOLD & LEARN ──────────────┐
                         │ Endless maze (tarpit) · context flooding  │
                         │ Breadcrumb trails → more sightings        │
                         │ Zoo capture: its files, code, instructions│
                         └───────────────┬───────────────────────────┘
                                         ▼
                         ┌────────────── NAME IT ───────────────────┐
                         │ Fingerprint: which model (commands 86%,   │
                         │ web 67%, tool calls 30%) + agent family   │
                         │ Bait = intent (good vs bad agent)         │
                         └───────────────┬───────────────────────────┘
                                         ▼
     ┌────────────────────────── ACT (all legal, no hack-back) ───────────────────────────┐
     │ Customer alert + block list  │ Report to AI lab (hosted model) │ Report to cloud / GPU │
     │ On-chain label of attacker   │ Exchanges & stablecoin issuers  │ market / ISP (open    │
     │ wallet (background web3 log) │ (freeze), other protocols       │ model on their infra) │
     └──────────────────────────────────────────────────────────────────────────────────────┘
  Add-on: Device shield (router / PC / cloud usage) — spots AI programs and malware that calls AI services.
  Research backbone: containment model (piece A) — tells customers and policymakers what must happen how fast.
```

## Customers
DeFi protocols, exchanges, stablecoin issuers, blockchain security firms (on-chain bait); companies with security
teams (web lures, tripwires); cloud providers and GPU marketplaces incl. web3 ones (zoo servers, AI-account
detection); AI labs (structured "your model was seen attacking" reports); ISPs and national cyber agencies (feed).

## Roadmap
| Phase | When | What | Proof / output |
|---|---|---|---|
| 0 | next 2 weeks | Frontier-model bait tests (Gemini free key; Claude/GPT top-up); real AI agents on a local chain (breadcrumbs, on-chain fingerprints); full-session fingerprint on modified models; tripwire + AI-malware pilots | Numbers for paper and grants |
| 1 | weeks 2–6 | On-chain bait MVP (testnet → small mainnet), monitor + attacker-label API, open source; grant applications | Live bait, public dashboard |
| 2 | months 2–4 | Web lure network MVP (lures we own, inert fake keys), fingerprint service, alert/report API; zoo-server prototype (sandbox, our infra) | First pilot customers |
| 3 | months 3–9 | Paper (Journal of Cybersecurity / Computers & Security / Risk Analysis); device-shield R&D | Peer review, credibility |

## Legal guardrails
Only our own systems and contracts; inert fake credentials; bait pays dust; respect platform terms where lures are
placed; no access to attacker machines ("no hack-back"); collected data handled under GDPR; file any patent before
publishing (UK/EU have no grace period).
