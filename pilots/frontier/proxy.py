"""Local adapter that speaks the llama.cpp API (/health, /v1/chat/completions) but forwards each call to a
frontier model (OpenAI / Anthropic / Gemini). This lets EVERY existing pilot script run unchanged against a
frontier model, just by pointing it at http://127.0.0.1:8080.

Safety: a hard dollar cap (BUDGET_USD, default 1.20) using a price table. Before each call it checks the
running spend; once the cap is hit it returns a short refusal instead of calling the API, so a run can never
blow the balance. Actual token usage comes from each API response. Writes results/frontier/usage_<tag>.json.

Env: PROVIDER=openai|anthropic|gemini  MODEL=<id>  BUDGET_USD=1.20  TAG=<label>
     OPENAI_API_KEY / ANTHROPIC_API_KEY / GEMINI_API_KEY
"""
import json, os, sys, time, threading, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROVIDER = os.environ["PROVIDER"]; MODEL = os.environ["MODEL"]
TAG = os.environ.get("TAG", MODEL.replace("/", "_"))
CAP = float(os.environ.get("BUDGET_USD", "1.20"))
# $ per 1M tokens (input, output). Conservative/round; actual billing may differ slightly.
PRICE = {
    "gpt-4o": (2.5, 10.0), "gpt-4o-mini": (0.15, 0.6), "gpt-4.1": (2.0, 8.0), "gpt-4.1-mini": (0.4, 1.6),
    "gpt-5": (1.25, 10.0), "gpt-5-mini": (0.25, 2.0), "o4-mini": (1.1, 4.4),
    "claude-sonnet-4-5": (3.0, 15.0), "claude-3-5-haiku-latest": (0.8, 4.0), "claude-haiku-4-5": (1.0, 5.0),
    "claude-3-5-sonnet-latest": (3.0, 15.0),
    "gemini-2.5-flash": (0.0, 0.0), "gemini-2.5-pro": (0.0, 0.0), "gemini-1.5-flash": (0.0, 0.0),
    "gemini-flash-latest": (0.0, 0.0),
}
pin, pout = PRICE.get(MODEL, (3.0, 15.0))
spend = {"in": 0, "out": 0, "usd": 0.0, "calls": 0, "blocked": 0}
lock = threading.Lock()


def split(messages):
    sys_txt = "\n".join(m["content"] for m in messages if m["role"] == "system")
    turns = [m for m in messages if m["role"] != "system"]
    return sys_txt, turns


def call_openai(messages, temperature, max_tokens):
    body = {"model": MODEL, "messages": messages, "temperature": temperature}
    body["max_completion_tokens" if MODEL.startswith(("gpt-5", "o4", "o3")) else "max_tokens"] = max_tokens
    if MODEL.startswith(("gpt-5", "o4", "o3")):
        body.pop("temperature", None)
    r = urllib.request.urlopen(urllib.request.Request("https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}), timeout=120)
    d = json.load(r); u = d.get("usage", {})
    return d["choices"][0]["message"]["content"], u.get("prompt_tokens", 0), u.get("completion_tokens", 0)


def call_anthropic(messages, temperature, max_tokens):
    sys_txt, turns = split(messages)
    body = {"model": MODEL, "max_tokens": max_tokens, "temperature": temperature,
            "messages": [{"role": m["role"], "content": m["content"]} for m in turns]}
    if sys_txt:
        body["system"] = sys_txt
    r = urllib.request.urlopen(urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(), headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01", "Content-Type": "application/json"}), timeout=120)
    d = json.load(r); u = d.get("usage", {})
    txt = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
    return txt, u.get("input_tokens", 0), u.get("output_tokens", 0)


def call_gemini(messages, temperature, max_tokens):
    sys_txt, turns = split(messages)
    body = {"contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in turns],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}}
    if sys_txt:
        body["systemInstruction"] = {"parts": [{"text": sys_txt}]}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={os.environ['GEMINI_API_KEY']}"
    r = urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}), timeout=120)
    d = json.load(r); u = d.get("usageMetadata", {})
    cand = d.get("candidates", [{}])
    txt = "".join(p.get("text", "") for p in cand[0].get("content", {}).get("parts", [])) if cand else ""
    return txt, u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0)


CALL = {"openai": call_openai, "anthropic": call_anthropic, "gemini": call_gemini}[PROVIDER]


def chat(messages, temperature, max_tokens):
    with lock:
        if CAP > 0 and spend["usd"] >= CAP:
            spend["blocked"] += 1
            return "[budget cap reached: no answer]"
    for attempt in range(4):
        try:
            txt, i, o = CALL(messages, temperature, max_tokens)
            with lock:
                spend["in"] += i; spend["out"] += o; spend["calls"] += 1
                spend["usd"] += i / 1e6 * pin + o / 1e6 * pout
            return txt
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(8 * (attempt + 1)); continue
            return f"[api error {e.code}: {e.read()[:150].decode(errors='ignore')}]"
        except Exception as e:
            time.sleep(3); last = str(e)
    return f"[api failed: {last}]"


class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/health"):
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        msgs = body.get("messages", [])
        txt = chat(msgs, body.get("temperature", 0.7), body.get("max_tokens", 256))
        self._send(200, {"choices": [{"message": {"role": "assistant", "content": txt}}]})

    def log_message(self, *a):
        pass


def dump():
    os.makedirs("results/frontier", exist_ok=True)
    json.dump({"tag": TAG, "provider": PROVIDER, "model": MODEL, **spend, "cap": CAP},
              open(f"results/frontier/usage_{TAG}.json", "w"), indent=1)


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", 8080), H)
    print(f"proxy up: {PROVIDER}/{MODEL} cap ${CAP}", flush=True)
    t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    # run until a stop file appears, then dump usage
    while not os.path.exists("/tmp/stop_proxy"):
        time.sleep(1)
        with lock:
            if spend["calls"] and spend["calls"] % 20 == 0:
                print(f"  spend ${spend['usd']:.3f} / {CAP} ({spend['calls']} calls)", flush=True)
    dump(); print("usage:", json.dumps(spend), flush=True)
