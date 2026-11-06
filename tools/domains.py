"""Check .com / .ai / .io registration via RDAP (404 = not registered = likely available)."""
import json, sys, time, urllib.request, urllib.error
EP = {"com": "https://rdap.verisign.com/com/v1/domain/{}.com"}
def status(url):
    for _ in range(3):
        try:
            urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/rdap+json"}), timeout=20)
            return "taken"
        except urllib.error.HTTPError as e:
            if e.code == 404: return "free"
            if e.code == 429: time.sleep(5); continue
            return f"?{e.code}"
        except Exception as e:
            time.sleep(2)
    return "?"
out = ["| Group | Name | .com |", "|---|---|---|"]
for line in open(sys.argv[1]):
    g, n = line.strip().split("|")
    r = {t: status(u.format(n)) for t, u in EP.items()}
    out.append(f"| {g} | {n} | {r['com']} |"); print(out[-1], flush=True); time.sleep(1)
open("tools/DOMAINS.md", "w").write("\n".join(out) + "\n")
