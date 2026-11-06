"""Download every URL in pilots/humanoid/urls.txt into data/humanoid/raw/ (runs on GitHub Actions)."""
import hashlib, os, re, urllib.request

os.makedirs("data/humanoid/raw", exist_ok=True)
for u in open("pilots/humanoid/urls.txt").read().split():
    name = re.sub(r"[^A-Za-z0-9]+", "_", re.sub(r"^https?://", "", u))[:90] + "_" + hashlib.md5(u.encode()).hexdigest()[:6]
    ext = ".csv" if "output=csv" in u else ".html"
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (research data collection)"})
        body = urllib.request.urlopen(req, timeout=60).read()
        open(f"data/humanoid/raw/{name}{ext}", "wb").write(body)
        print(200, len(body), u)
    except Exception as e:
        print("ERR", e, u)
