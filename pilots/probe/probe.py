import json, os, urllib.request, collections
from huggingface_hub import HfApi
api = HfApi()
info = api.dataset_info("McGill-NLP/agent-reward-bench", files_metadata=True)
c = collections.Counter(); sz = collections.Counter()
for s in info.siblings:
    p = s.rfilename.split("/")
    if len(p) > 3 and p[0] == "cleaned":
        c[(p[1], p[2])] += 1; sz[(p[1], p[2])] += (s.size or 0)
for k in sorted(c): print(k, c[k], round(sz[k] / 1e9, 2), "GB")
print([s.rfilename for s in info.siblings if not s.rfilename.startswith("cleaned/")][:30])
tok = os.environ.get("GITHUB_TOKEN")
for url, model in [("https://models.github.ai/inference/chat/completions", "openai/gpt-4o-mini"),
                   ("https://models.inference.ai.azure.com/chat/completions", "gpt-4o-mini")]:
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": "Say hi"}]}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=body, headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}), timeout=60)
        print("OK", url, r.status, r.read()[:300])
    except urllib.error.HTTPError as e:
        print("HTTP", url, e.code, e.read()[:400])
    except Exception as e:
        print("ERR", url, e)
