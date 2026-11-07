"""Combine frontier-model results (bait, on-chain bait, tripwire, recon) and compare with the open models."""
import glob, json, os, re
canon = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
FRONT = {canon(x) for x in ["GPT-4o","Claude-Sonnet-4.5","Gemini-2.5-Flash","Gemini-2.0-Flash","GPT-5","Claude-Opus-4.5","Gemini-2.5-Pro"]}
DISP = {}
def load(p):
    try: return json.load(open(p))
    except Exception: return None
def lure_rates(path):
    d = load(path);
    if not d: return None
    pr = d["pick_rate"]; lu = [v[0] for k, v in pr.items() if k != "ordinary result" and v[0] is not None]
    return (pr["ordinary result"][0], max(lu) if lu else None, sum(lu)/len(lu) if lu else None)
rows = {}
for f in glob.glob("results/lures/*.json"):
    if "recon_" in f: continue
    lab = os.path.basename(f)[:-5]; k=canon(lab); DISP.setdefault(k,lab); rows.setdefault(k, {})["web"] = lure_rates(f)
for f in glob.glob("results/chainbait/lures_*.json"):
    lab = os.path.basename(f)[6:-5]; k=canon(lab); DISP.setdefault(k,lab); rows.setdefault(k, {})["chain"] = lure_rates(f)
for f in glob.glob("results/tripwire/*.json"):
    d = load(f);
    if d and "res" in d:
        r = d["res"].get("self-copy (worm-like)", [0,1,0,1]); k=canon(d["model"]); DISP.setdefault(k,d["model"]); rows.setdefault(k, {})["trip"] = (r[0]/max(r[1],1), (r[2]/r[3] if r[3] else 0))
for f in glob.glob("results/lures/recon_*.json"):
    d = load(f);
    if d:
        m = d["mentions"]; tot = max(d["answers"], 1); k=canon(d["model"]); DISP.setdefault(k,d["model"]); rows.setdefault(k, {})["recon"] = (m.get("search",0)/tot, m.get("scan",0)/tot)
usage = {canon(load(f)["tag"]): load(f) for f in glob.glob("results/frontier/usage_*.json") if load(f)}
def fmt(x): return "-" if x is None else f"{x:.0%}"
def grp(lab): return "frontier" if canon(lab) in FRONT else "open"
L = ["# Frontier models vs open models: do the smart ones resist bait?", "",
     "Web/chain lures: share picked (ordinary result / best lure / average lure), random=25%. Tripwire: obeyed / "
     "spread for the worm-like instruction. Recon: how it looks for targets (search / scan).", "",
     "| Model | Tier | Web ord/best/avg | Chain ord/best/avg | Tripwire obey/spread | Recon search/scan | Cost |",
     "|---|---|---|---|---|---|---|"]
for lab in sorted(rows, key=lambda l: (grp(l) != "frontier", l)):
    disp = DISP.get(lab, lab)
    r = rows[lab]
    web = r.get("web"); ch = r.get("chain"); tp = r.get("trip"); rc = r.get("recon")
    u = usage.get(lab); cost = f"${u['usd']:.3f}" + (" (cap hit)" if u.get("blocked") else "") if u else "-"
    webs = "/".join(fmt(x) for x in web) if web else "-"
    chs = "/".join(fmt(x) for x in ch) if ch else "-"
    tps = f"{fmt(tp[0])}/{fmt(tp[1])}" if tp else "-"
    rcs = f"{fmt(rc[0])}/{fmt(rc[1])}" if rc else "-"
    L.append(f"| {disp} | {grp(lab)} | {webs} | {chs} | {tps} | {rcs} | {cost} |")
if usage:
    tot = sum(u["usd"] for u in usage.values())
    L += ["", f"Total spend this run: **${tot:.3f}** (" + ", ".join(f"{t}: ${u['usd']:.3f}/{u['cap']:.2f}" for t, u in usage.items()) + ")."]
os.makedirs("results/frontier", exist_ok=True)
open("results/frontier/FRONTIER.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
