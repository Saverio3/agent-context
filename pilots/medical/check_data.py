"""Check which open datasets exist for the medical pilots and fetch the small ones.
- Wastewater + hospital admissions (US CDC open data portal, Socrata catalog search)
- Paediatric and adult chest X-ray, longitudinal chest X-ray (just record availability)"""
import json, os, urllib.request, urllib.parse
os.makedirs("data/medical", exist_ok=True)
H = {"User-Agent": "research-pilot"}


def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60).read())


out = {}
for q in ["wastewater SARS-CoV-2", "NWSS", "hospital admissions COVID weekly", "respiratory hospital"]:
    try:
        r = get("https://api.us.socrata.com/api/catalog/v1?domains=data.cdc.gov&limit=15&q=" + urllib.parse.quote(q))
        out[q] = [(x["resource"]["id"], x["resource"]["name"], x["resource"].get("data_updated_at")) for x in r["results"]]
    except Exception as e:
        out[q] = str(e)
json.dump(out, open("data/medical/cdc_catalog.json", "w"), indent=1)
for q, v in out.items():
    print("==", q)
    for x in (v if isinstance(v, list) else [v])[:15]:
        print("  ", x)
