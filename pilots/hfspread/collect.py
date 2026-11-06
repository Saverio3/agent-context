"""Collect Hugging Face model family trees: for popular base models from major labs, every derivative
(fine-tune, adapter, quantisation, merge) with its creation date and author. -> data/hfspread/*.json"""
import json, os, re, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

ORGS = ["meta-llama", "Qwen", "mistralai", "google", "microsoft", "deepseek-ai", "HuggingFaceTB", "ibm-granite",
        "allenai", "nvidia", "openai", "moonshotai", "zai-org", "tiiuae", "CohereLabs", "THUDM", "01-ai", "internlm",
        "stabilityai", "apple", "black-forest-labs", "LiquidAI", "baidu", "tencent", "unsloth"]
API = "https://huggingface.co/api/models"
HDR = {"User-Agent": "research-pilot"}
if os.environ.get("HF_TOKEN"):
    HDR["Authorization"] = "Bearer " + os.environ["HF_TOKEN"]


def get(url):
    for k in range(5):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=60)
            link = r.headers.get("Link", "")
            return json.loads(r.read()), (re.search(r'<([^>]+)>;\s*rel="next"', link) or [None, None])[1]
        except Exception as e:
            time.sleep(2 + 3 * k); err = e
    print("FAIL", url, err); return [], None


def main(cap=20000):
    os.makedirs("data/hfspread", exist_ok=True)
    bases = []
    for org in ORGS:
        items, _ = get(f"{API}?author={org}&sort=downloads&direction=-1&limit=30&full=true")
        for m in items:
            bases.append(m["id"])
    print("candidate bases", len(bases))
    out = []
    for b in bases:
        info, _ = get(f"{API}/{urllib.parse.quote(b, safe='/')}")
        if not isinstance(info, dict) or "createdAt" not in info:
            continue
        created = info["createdAt"]
        url = f"{API}?filter={urllib.parse.quote('base_model:' + b, safe='')}&sort=createdAt&direction=1&limit=1000"
        ders, n = [], 0
        while url and len(ders) < cap:
            items, url = get(url)
            ders += [(d.get("createdAt"), d["id"].split("/")[0], [t for t in d.get("tags", []) if t.startswith("base_model:")][:2]) for d in items]
        out.append({"base": b, "createdAt": created, "pipeline": info.get("pipeline_tag"),
                    "derivatives": ders, "capped": len(ders) >= cap})
        print(b, created[:10], len(ders), flush=True)
    json.dump(out, open("data/hfspread/trees.json", "w"))


if __name__ == "__main__":
    main()
