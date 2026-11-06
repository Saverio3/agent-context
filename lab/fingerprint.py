"""Pilot: can we tell WHICH AI model ran an agent session from its behaviour alone,
and can we predict WHAT IT DOES NEXT from its fingerprint?

Data: public SWE-agent runs (data/nebius.jsonl), each labelled with the model that ran it.
Tasks are split so the test set only contains tasks never seen in training
(the detector cannot cheat by recognising the bug).

Part A - identify the model: behaviour features only (which commands it uses, how long its
         messages are, how it phrases things, its rhythm), never the task text or the label.
Part B - predict the next move: given the last 3 commands, predict the next command type.
         Compare a generic predictor (trained on all models) with one that first identifies
         the model and then uses that model's own habits.

python -m lab.fingerprint --jsonl data/nebius.jsonl --out results/nebius/fingerprint
"""
import argparse
import json
import os
import re
import zlib
from collections import Counter, defaultdict

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix

from .core import _norm_role

CMD = re.compile(r"```(?:bash|sh)?\s*\n(.*?)```", re.S)
WORD = re.compile(r"[A-Za-z_]+")
STYLE_WORDS = ["let's", "now", "i'll", "first", "great", "looks", "seems", "need", "should", "will",
               "however", "perfect", "excellent", "issue", "fix", "verify", "test", "check", "next", "done"]


def family(model):
    m = model.lower()
    for k in ("claude", "gpt-4o", "gpt-4", "gpt", "o1", "o3", "qwen", "llama", "deepseek", "mistral", "gemini"):
        if k in m:
            return k
    return m.split("/")[-1][:20] or "unknown"


def commands(text):
    """first word of every shell command the agent issued in this message"""
    out = []
    for block in CMD.findall(text):
        for line in block.strip().splitlines():
            w = line.strip().split()
            if w:
                out.append(w[0].strip("$")[:20])
    if not out:  # SWE-agent sometimes writes the command as the last line, no fence
        last = text.strip().splitlines()[-1:] if text.strip() else []
        if last and re.match(r"^[a-z_]+(\s|$)", last[0]):
            out.append(last[0].split()[0][:20])
    return out


def features(msgs):
    asst = [t for r, t in msgs if r == "assistant"]
    tool = [t for r, t in msgs if r == "tool"]
    f = Counter()
    cmds = [c for t in asst for c in commands(t)]
    for c in cmds:
        f["cmd=" + c] += 1
    n = max(1, len(cmds))
    for k in list(f):
        f[k] /= n
    for a, b in zip(cmds, cmds[1:]):
        f[f"bigram={a}>{b}"] += 1 / n
    lens = [len(t) for t in asst] or [0]
    f["n_steps"] = len(asst)
    f["len_mean"] = float(np.mean(lens))
    f["len_med"] = float(np.median(lens))
    f["len_max"] = float(max(lens))
    f["tool_len_mean"] = float(np.mean([len(t) for t in tool] or [0]))
    text = " ".join(asst).lower()
    words = max(1, len(WORD.findall(text)))
    for w in STYLE_WORDS:
        f["w=" + w] = text.count(w) / words * 1000
    f["newlines_per_msg"] = text.count("\n") / max(1, len(asst))
    f["bullets"] = text.count("\n- ") / max(1, len(asst))
    f["backticks"] = text.count("`") / max(1, len(asst))
    f["exclaim"] = text.count("!") / words * 1000
    f["question"] = text.count("?") / words * 1000
    f["first_person"] = len(re.findall(r"\bi\b|\bi'm\b|\bi'll\b", text)) / words * 1000
    f["uses_think_tag"] = 1.0 if "<thought" in text or "discussion" in text else 0.0
    return f, cmds


def task_of(rid):
    return rid.split(":")[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=6000)
    ap.add_argument("--min-runs", type=int, default=60)
    a = ap.parse_args()

    rows = []
    with open(a.jsonl) as fh:
        for line in fh:
            d = json.loads(line)
            parts = d["id"].split(":")
            model = parts[1] if len(parts) > 2 else ""
            if not model:
                continue
            ms, seen = [], False
            for role, text in d["messages"]:
                role, seen = _norm_role(role, seen)
                ms.append((role, text))
            if sum(r == "assistant" for r, _ in ms) < 4:
                continue
            f, cmds = features(ms)
            rows.append((d["id"], model, family(model), f, cmds))
            if len(rows) >= a.limit:
                break

    counts = Counter(r[1] for r in rows)
    keep = {m for m, c in counts.items() if c >= a.min_runs}
    rows = [r for r in rows if r[1] in keep]
    test = [r for r in rows if zlib.crc32(task_of(r[0]).encode()) % 4 == 0]   # unseen tasks
    train = [r for r in rows if zlib.crc32(task_of(r[0]).encode()) % 4 != 0]

    lines = [f"# Fingerprinting pilot — {len(rows)} runs, {len(keep)} models (≥{a.min_runs} runs each)", "",
             f"Train {len(train)} runs / test {len(test)} runs on tasks the detector never saw.", "",
             "| Model | Runs |", "|---|---|"] + [f"| {m} | {counts[m]} |" for m in sorted(keep, key=lambda m: -counts[m])]

    # ---------- Part A ----------
    dv = DictVectorizer(sparse=False)
    Xtr = dv.fit_transform([r[3] for r in train])
    Xte = dv.transform([r[3] for r in test])
    for label_idx, label_name in ((1, "exact model"), (2, "model family")):
        ytr = [r[label_idx] for r in train]
        yte = [r[label_idx] for r in test]
        if len(set(ytr)) < 2:
            continue
        clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, random_state=0)
        clf.fit(Xtr, ytr)
        pred = clf.predict(Xte)
        proba = clf.predict_proba(Xte)
        top2 = np.mean([y in clf.classes_[np.argsort(p)[-2:]] for y, p in zip(yte, proba)])
        chance = max(Counter(yte).values()) / len(yte)
        lines += ["", f"## A. Identify the {label_name} ({len(set(ytr))} classes)", "",
                  f"- Accuracy on unseen tasks: **{accuracy_score(yte, pred):.1%}** (top-2: {top2:.1%})",
                  f"- Always guessing the most common class: {chance:.1%}"]
        # accuracy using only the first 5 steps (how fast can we recognise it?)
        if label_idx == 1:
            cm = confusion_matrix(yte, pred, labels=clf.classes_)
            per = {c: cm[i, i] / max(1, cm[i].sum()) for i, c in enumerate(clf.classes_)}
            lines += ["", "| Model | Recognised correctly |", "|---|---|"] + \
                     [f"| {c} | {v:.0%} |" for c, v in sorted(per.items(), key=lambda kv: -kv[1])]

    # ---------- Part B: predict the next command ----------
    def ngram_model(runs):
        m = defaultdict(Counter)
        for r in runs:
            c = r[4]
            for i in range(3, len(c)):
                m[tuple(c[i - 3:i])][c[i]] += 1
                m[tuple(c[i - 1:i])][c[i]] += 1
                m[()][c[i]] += 1
        return m

    def predict(m, hist):
        for k in (tuple(hist[-3:]), tuple(hist[-1:]), ()):
            if m.get(k):
                return m[k].most_common(1)[0][0]
        return None

    generic = ngram_model(train)
    per_model = {mdl: ngram_model([r for r in train if r[1] == mdl]) for mdl in keep}
    hit_g = hit_m = tot = 0
    for r in test:
        c = r[4]
        for i in range(3, len(c)):
            tot += 1
            hit_g += predict(generic, c[:i]) == c[i]
            pm = per_model[r[1]]
            hit_m += (predict(pm, c[:i]) or predict(generic, c[:i])) == c[i]
    if tot:
        lines += ["", "## B. Predict the agent's next command", "",
                  f"- Generic predictor (all models pooled): **{hit_g / tot:.1%}** of next commands right",
                  f"- Knowing which model it is: **{hit_m / tot:.1%}**",
                  f"- {tot:,} predictions on unseen tasks. Upper bound for B: assumes the model was identified correctly."]

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "FINGERPRINT.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
