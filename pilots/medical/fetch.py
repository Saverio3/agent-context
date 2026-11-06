"""Fetch CDC open data for the wastewater space-time pilot (runs on GitHub Actions)."""
import os, urllib.request
os.makedirs("data/medical", exist_ok=True)
for rid, name in [("atcp-73re", "wastewater_levels"), ("ua7e-t2fy", "hospital_weekly"), ("j9g8-acpt", "wastewater_covid_sites")]:
    url = f"https://data.cdc.gov/resource/{rid}.csv?$limit=2000000"
    body = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-pilot"}), timeout=600).read()
    open(f"data/medical/{name}.csv", "wb").write(body)
    print(name, len(body), "bytes", body[:400])
