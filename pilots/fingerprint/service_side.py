"""Pilot C: can a WEBSITE or an API/TOOL SERVICE tell which AI model is driving the agent?

Only what that service would see is used — never the agent's reasoning.
  web   : AgentRewardBench browser-agent runs (WebArena, WorkArena, AssistantBench; GPT-4o, Claude 3.7 Sonnet,
          Llama 3.3 70B, Qwen2.5-VL 72B). Visible to the site: actions (click / type / scroll / go to URL),
          the text typed, scroll sizes, number of steps.
  tools : tau-bench runs from ~30 model configs (GPT-4o/4.1/5, o3, Claude 4/4.5, Gemini 2.5, DeepSeek, Qwen3, Kimi K2,
          gpt-oss). Visible to the service: tool names called, argument JSON (keys, order, formatting, values).
Train/test split by task, so test tasks were never seen in training.
Usage: python service_side.py web <dir> | tools <dir>
"""
import glob
import json
import os
import re
import sys
import zlib
from collections import Counter, defaultdict

from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

MODE, ROOT = sys.argv[1], sys.argv[2]


def walk(o, key, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key and isinstance(v, str):
                out.append(v)
            else:
                walk(v, key, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, key, out)
    return out


def web_runs():
    runs = []
    for f in glob.glob(f"{ROOT}/**/*.json", recursive=True):
        m = re.search(r"GenericAgent-([^/]+?)/", f)
        if not m:
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        acts = walk(d, "action", [])
        acts = [a for a in acts if a and len(a) < 2000]
        if len(acts) >= 2:
            task = os.path.basename(f).rsplit(".", 1)[0]
            runs.append((m.group(1), task, acts))
    if runs:
        print("example actions:", runs[0][0], runs[0][2][:6])
    return runs


def web_doc(acts):
    toks = []
    for a in acts:
        verb = re.match(r"\s*([a-z_]+)\(", a)
        v = verb.group(1) if verb else "other"
        toks.append(f"V_{v}")
        for s in re.findall(r"'([^']*)'|\"([^\"]*)\"", a):
            s = s[0] or s[1]
            if not re.fullmatch(r"[a-z]?\d+", s):  # skip element ids, keep typed text / URLs
                toks.append(s)
        for n in re.findall(r"-?\d+", a):
            if v.startswith("scroll"):
                toks.append(f"SCROLL_{n}")
    vs = [t for t in toks if t.startswith("V_")]
    toks += [f"P_{a}_{b}" for a, b in zip(vs, vs[1:])] + [f"LEN_{min(len(acts), 30) // 5}"]
    return toks


def tool_runs():
    runs = []
    for f in glob.glob(f"{ROOT}/**/*.jsonl", recursive=True):
        model = os.path.basename(f)[:-6]
        for i, line in enumerate(open(f)):
            try:
                d = json.loads(line)
            except Exception:
                continue
            calls = []
            def find(o):
                if isinstance(o, dict):
                    if "name" in o and "arguments" in o and isinstance(o["name"], str):
                        a = o["arguments"]
                        calls.append((o["name"], a if isinstance(a, str) else json.dumps(a)))
                    for v in o.values():
                        find(v)
                elif isinstance(o, list):
                    for v in o:
                        find(v)
            find(d)
            task = str(d.get("task_id", d.get("id", i)))
            if len(calls) >= 1:
                runs.append((model, task, calls))
    if runs:
        print("example calls:", runs[0][0], runs[0][2][:4])
    return runs


def tool_doc(calls):
    toks = []
    for n, a in calls:
        toks.append(f"T_{n}")
        toks += [f"K_{k}" for k in re.findall(r'"([A-Za-z_]+)"\s*:', a)]
        toks.append("SP_" + ("compact" if '":"' in a or '",' in a.replace('", ', '') else "spaced"))
    ns = [n for n, _ in calls]
    toks += [f"P_{a}_{b}" for a, b in zip(ns, ns[1:])] + [f"LEN_{min(len(calls), 30) // 3}"]
    return toks


runs = web_runs() if MODE == "web" else tool_runs()
fam = (lambda m: m) if MODE == "web" else (lambda m: re.sub(r"-thinking-(on|off).*|-high$", "", m))
runs = [(fam(m), t, x) for m, t, x in runs]
cnt = Counter(m for m, _, _ in runs)
keep = {m for m, k in cnt.items() if k >= 30}
runs = [r for r in runs if r[0] in keep]
test = lambda t: zlib.crc32(t.encode()) % 4 == 0
tr = [r for r in runs if not test(r[1])]; te = [r for r in runs if test(r[1])]
doc = web_doc if MODE == "web" else tool_doc
raw = (lambda x: "\n".join(x)) if MODE == "web" else (lambda x: "\n".join(f"{n}({a})" for n, a in x))
v1 = TfidfVectorizer(analyzer=lambda d: d, min_df=2, sublinear_tf=True)
v2 = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, max_features=150000, sublinear_tf=True)
Xtr = hstack([v1.fit_transform([doc(x) for _, _, x in tr]), v2.fit_transform([raw(x) for _, _, x in tr])]).tocsr()
clf = LogisticRegression(max_iter=4000, C=4.0, class_weight="balanced").fit(Xtr, [m for m, _, _ in tr])


def acc(n):
    cut = (lambda x: x[:n]) if n else (lambda x: x)
    X = hstack([v1.transform([doc(cut(x)) for _, _, x in te]), v2.transform([raw(cut(x)) for _, _, x in te])]).tocsr()
    p = clf.predict(X)
    return accuracy_score([m for m, _, _ in te], p), p


chance = max(cnt[m] for m in keep) / sum(cnt[m] for m in keep)
name = {"web": "a website", "tools": "an API / tool service"}[MODE]
out = [f"# Naming the AI model from what {name} sees ({MODE})", "",
       f"{len(runs)} runs, {len(keep)} models, split by task ({len(tr)} train / {len(te)} test). "
       f"Always guessing the most common model: {chance:.0%}; random: {1 / len(keep):.0%}.", "",
       "| Steps seen | Accuracy |", "|---|---|"]
for n in (3, 10, None):
    a, p = acc(n)
    out.append(f"| {'First ' + str(n) if n else 'Whole session'} | {a:.0%} |")
out += ["", "| Model | Test runs | Correct |", "|---|---|---|"]
per = defaultdict(lambda: [0, 0])
for (m, _, _), q in zip(te, p):
    per[m][1] += 1; per[m][0] += m == q
for m in sorted(per):
    out.append(f"| {m} | {per[m][1]} | {per[m][0] / per[m][1]:.0%} |")
os.makedirs("results/fingerprint", exist_ok=True)
open(f"results/fingerprint/SERVICE_{MODE.upper()}.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))
