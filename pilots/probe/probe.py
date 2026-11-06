import json, os, urllib.request
from huggingface_hub import HfApi
api = HfApi()
for repo in ["McGill-NLP/agent-reward-bench", "AgentSuite/tau-bench-trajectories"]:
    try:
        info = api.dataset_info(repo, files_metadata=True)
        fs = [(s.rfilename, s.size or 0) for s in info.siblings]
        print("==", repo, len(fs), "files", round(sum(s for _, s in fs) / 1e9, 2), "GB")
        for f, s in fs[:40]: print("  ", f, round(s / 1e6, 2), "MB")
    except Exception as e:
        print("fail", repo, e)
for q in ["agent trajectories web", "browser agent trajectories", "tau-bench"]:
    try:
        print("search", q, [d.id for d in api.list_datasets(search=q, limit=15)])
    except Exception as e: print("search fail", e)
tok = os.environ.get("GITHUB_TOKEN")
try:
    r = urllib.request.urlopen(urllib.request.Request("https://models.github.ai/catalog/models", headers={"Authorization": f"Bearer {tok}"}), timeout=30)
    cat = json.load(r); print("catalog", len(cat)); print([m.get("id") for m in cat][:80])
except Exception as e:
    print("catalog fail", e)
body = json.dumps({"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": "Say hi"}]}).encode()
try:
    r = urllib.request.urlopen(urllib.request.Request("https://models.github.ai/inference/chat/completions", data=body,
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}), timeout=60)
    print("inference ok", json.load(r)["choices"][0]["message"]["content"], dict(r.headers).get("x-ratelimit-remaining-requests"))
except Exception as e:
    print("inference fail", e, getattr(e, "read", lambda: b"")()[:300])
