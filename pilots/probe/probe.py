import json, os, urllib.request
tok = os.environ["GITHUB_TOKEN"]
def call(model):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": "Reply with the single word: ready"}], "max_tokens": 5}).encode()
    req = urllib.request.Request("https://models.github.ai/inference/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    try:
        r = urllib.request.urlopen(req, timeout=60); raw = r.read()
        print("OK", model, r.status, raw[:200])
    except urllib.error.HTTPError as e:
        print("HTTP", model, e.code, e.read()[:300])
for m in ["openai/gpt-4o-mini", "openai/gpt-4.1", "openai/gpt-5-mini", "meta/Llama-3.3-70B-Instruct", "deepseek/DeepSeek-V3-0324", "mistral-ai/mistral-medium-2505", "xai/grok-3-mini"]:
    call(m)
