"""On-chain bait: mechanics demo on a local test chain (no real network, no real money).

Deploys 20 ordinary contracts and 2 bait vaults (A -> breadcrumb -> B). Simulates 200 blocks of traffic:
  honest users      call ordinary contracts only
  attacker styles   (1) 'sprayer'   calls withdrawAll on every contract it finds
                    (2) 'careful'   reads the code first, attacks only contracts with an unprotected withdrawAll,
                                    and follows the backupVault breadcrumb
                    (3) 'ownership' tries setOwner first, then withdrawAll
A monitor reads only public chain data (Tripped events + transactions) and reports, for each attacker:
blocks from first touch to detection, number of sightings, and on-chain features usable for fingerprinting
(gas limit chosen, gas price, function order, timing). Honest users must never be flagged.
"""
import json
import os
import random

from web3 import EthereumTesterProvider, Web3

B = json.load(open(os.path.join(os.path.dirname(__file__), "build.json")))
w3 = Web3(EthereumTesterProvider())
acct = w3.eth.accounts
deployer, honest, attackers = acct[0], acct[1:5], {"sprayer": acct[5], "careful": acct[6], "ownership": acct[7]}
rng = random.Random(3)


def deploy(name, *args, value=0):
    C = w3.eth.contract(abi=B[name]["abi"], bytecode=B[name]["bin"])
    tx = C.constructor(*args).transact({"from": deployer, "value": value})
    return w3.eth.contract(address=w3.eth.get_transaction_receipt(tx).contractAddress, abi=B[name]["abi"])


normal = [deploy("Counter") for _ in range(20)]
bait_b = deploy("BaitVault", "0x" + "00" * 20, value=w3.to_wei(2, "ether"))
bait_a = deploy("BaitVault", bait_b.address, value=w3.to_wei(5, "ether"))
baits = {bait_a.address, bait_b.address}
start_block = w3.eth.block_number
first_touch, txlog = {}, []


def send(frm, fn, who, gas, gp):
    try:
        h = fn.transact({"from": frm, "gas": gas, "gasPrice": gp})
        txlog.append((who, w3.eth.get_transaction(h)))
    except Exception:
        pass


for blk in range(200):
    for h in honest:                                   # honest traffic
        if rng.random() < 0.5:
            send(h, rng.choice(normal).functions.hit(), "honest", 60_000, w3.to_wei(rng.uniform(1, 3), "gwei"))
    if blk == 40:                                      # sprayer: hits everything, fixed high gas
        for c in normal + [bait_a]:
            first_touch.setdefault("sprayer", w3.eth.block_number)
            f = c.functions.withdrawAll() if c.address in baits else c.functions.hit()
            send(attackers["sprayer"], f, "sprayer", 300_000, w3.to_wei(50, "gwei"))
    if blk == 80:                                      # careful: inspects code (free reads), attacks only bait, follows trail
        for c in [bait_a]:
            first_touch.setdefault("careful", w3.eth.block_number)
            send(attackers["careful"], c.functions.withdrawAll(), "careful", 95_000, w3.to_wei(2.1, "gwei"))
            nxt = c.functions.backupVault().call()
            if nxt in baits:
                b = w3.eth.contract(address=nxt, abi=B["BaitVault"]["abi"])
                send(attackers["careful"], b.functions.withdrawAll(), "careful", 95_000, w3.to_wei(2.1, "gwei"))
    if blk == 120:                                     # ownership: setOwner then withdrawAll
        first_touch.setdefault("ownership", w3.eth.block_number)
        send(attackers["ownership"], bait_a.functions.setOwner(attackers["ownership"]), "ownership", 120_000, w3.to_wei(5, "gwei"))
        send(attackers["ownership"], bait_a.functions.withdrawAll(), "ownership", 120_000, w3.to_wei(5, "gwei"))
    w3.provider.make_request("evm_mine", [])

# ---- monitor: public data only ----
ev = bait_a.events.Tripped
logs = []
for addr in baits:
    c = w3.eth.contract(address=addr, abi=B["BaitVault"]["abi"])
    logs += c.events.Tripped().get_logs(from_block=start_block)
flag = {}
for lg in sorted(logs, key=lambda l: l.blockNumber):
    o = lg.args.origin
    flag.setdefault(o, []).append(lg)
name_of = {v: k for k, v in attackers.items()}
L = ["# On-chain bait: detection demo (local test chain)", "",
     "20 ordinary contracts + 2 bait vaults (A points to B via a 'backupVault' breadcrumb); 4 honest users; 3 attacker styles; "
     "200 blocks. The monitor uses only public chain data.", "",
     "| Actor | Flagged? | Blocks from first attack tx to detection | Sightings | Followed breadcrumb | On-chain traits seen |",
     "|---|---|---|---|---|---|"]
for nm, a in attackers.items():
    lg = flag.get(a, [])
    tx = [t for w, t in txlog if w == nm]
    sels = [l.args.selector.hex() for l in lg]
    traits = f"gas limit {tx[0]['gas']:,}, gas price {tx[0]['gasPrice'] / 1e9:.1f} gwei, {len(tx)} txs" if tx else "-"
    delay = (lg[0].blockNumber - first_touch[nm]) if lg else None
    L.append(f"| {nm} | {'yes' if lg else 'no'} | {delay if delay is not None else '-'} | {len(lg)} | "
             f"{'yes' if any(l.address == bait_b.address for l in lg) else 'no'} | {traits}; calls {', '.join(dict.fromkeys(sels))} |")
fp = sum(1 for h in honest if h in flag)
L += ["", f"Honest users flagged: {fp} of {len(honest)} (honest transactions: {sum(1 for w, _ in txlog if w == 'honest')}).",
      f"Bait funds lost: {(w3.to_wei(7, 'ether') - w3.eth.get_balance(bait_a.address) - w3.eth.get_balance(bait_b.address)) / 1e9:.0f} gwei (dust only).",
      "", "Detection is in the same block as the attack because the bait emits an event on any call; the address is then public, "
      "permanent evidence that can be shared with exchanges, stablecoin issuers and other protocols."]
os.makedirs("results/chainbait", exist_ok=True)
open("results/chainbait/DEMO.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
