import json, os, requests
tok = os.environ["GITHUB_TOKEN"]
h = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
for url in ["https://models.github.ai/inference/chat/completions", "https://models.inference.ai.azure.com/chat/completions"]:
    for m in ["openai/gpt-4o-mini", "gpt-4o-mini"]:
        r = requests.post(url, headers=h, json={"model": m, "messages": [{"role": "user", "content": "Reply with the single word: ready"}], "max_tokens": 5}, allow_redirects=False, timeout=60)
        print(url, m, r.status_code, r.headers.get("location"), r.text[:200].replace("\n", " "))
print(requests.get("https://models.github.ai/catalog/models", headers=h, timeout=30).text[:300])
