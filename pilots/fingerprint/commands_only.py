"""Fingerprint re-test using ONLY what a decoy server would see: the shell commands.
No reasoning text, no phrasing. Same runs, same task-based train/test split as fingerprint.py.

Variants:
  verbs     - command names and pairs (e.g. grep, grep->sed)
  full      - the full command text: word and character patterns (flags, quoting, pipes, habits like
              '| head -50', '2>&1', heredocs)
Also scored on the first 3 / 10 commands, since a decoy may see only a few.
Usage: python commands_only.py data/mini.jsonl results/fingerprint
"""
import json
import os
import re
import sys
import zlib
from collections import Counter

from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

CODE = re.compile(r"```(?:bash|sh)?\n(.*?)```", re.S)
WORD = re.compile(r"[A-Za-z_][\w.-]*")


def commands(msgs):
    out = []
    for role, text in msgs:
        if role in ("assistant", "ai", "model"):
            b = CODE.findall(text)
            if b and b[-1].strip():
                out.append(b[-1].strip())
    return out


def verb(cmd):
    for seg in re.split(r"&&|\|\||;|\n", cmd):
        w = WORD.findall(seg)
        if w and w[0].lower() not in ("cd", "export", "set", "source"):
            return w[0].lower()
    return "none"


def verbs_doc(cmds):
    v = [verb(c) for c in cmds]
    return " ".join([f"A_{a}" for a in v] + [f"B_{a}_{b}" for a, b in zip(v, v[1:])])


def full_doc(cmds):
    return "\n".join(cmds)


def main(path, out):
    runs = []
    for line in open(path):
        d = json.loads(line)
        _, model, inst = (d["id"].split(":", 2) + ["", ""])[:3]
        inst = re.sub(r"[^A-Za-z0-9_.-].*$", "", inst) or inst
        c = commands(d["messages"])
        if len(c) >= 4 and model:
            runs.append((model, inst, c))
    cnt = Counter(m for m, _, _ in runs)
    keep = {m for m, k in cnt.items() if k >= 60}
    runs = [r for r in runs if r[0] in keep]
    test = lambda i: zlib.crc32(i.encode()) % 4 == 0
    tr = [r for r in runs if not test(r[1])]
    te = [r for r in runs if test(r[1])]
    ytr = [m for m, _, _ in tr]; yte = [m for m, _, _ in te]
    chance = max(cnt[m] for m in keep) / sum(cnt[m] for m in keep)

    vv = TfidfVectorizer(token_pattern=r"\S+", min_df=3, sublinear_tf=True)
    vw = TfidfVectorizer(token_pattern=r"[^\s]+", ngram_range=(1, 2), min_df=3, max_features=200000, sublinear_tf=True)
    vc = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=5, max_features=200000, sublinear_tf=True)
    Xv = vv.fit_transform([verbs_doc(c) for _, _, c in tr])
    Xf = hstack([vw.fit_transform([full_doc(c) for _, _, c in tr]), vc.fit_transform([full_doc(c) for _, _, c in tr])]).tocsr()
    cv = LogisticRegression(max_iter=3000, C=4.0, class_weight="balanced").fit(Xv, ytr)
    cf = LogisticRegression(max_iter=3000, C=4.0, class_weight="balanced").fit(Xf, ytr)

    def acc(n):
        cut = lambda c: c[:n] if n else c
        a = accuracy_score(yte, cv.predict(vv.transform([verbs_doc(cut(c)) for _, _, c in te])))
        docs = [full_doc(cut(c)) for _, _, c in te]
        b = accuracy_score(yte, cf.predict(hstack([vw.transform(docs), vc.transform(docs)]).tocsr()))
        return a, b

    lines = ["# Fingerprint from commands only (what a decoy server sees)", "",
             f"{len(runs)} runs, {len(keep)} models; split by task. Guessing the most common model: {chance:.1%}.", "",
             "| Commands seen | Command names only | Full command text |", "|---|---|---|"]
    for n, lab in ((3, "First 3"), (10, "First 10"), (25, "First 25"), (None, "Whole run")):
        a, b = acc(n)
        lines.append(f"| {lab} | {a:.1%} | {b:.1%} |")
    pf = cf.predict(hstack([vw.transform([full_doc(c) for _, _, c in te]), vc.transform([full_doc(c) for _, _, c in te])]).tocsr())
    lines += ["", "| Model | Test runs | Correct (full text, whole run) |", "|---|---|---|"]
    for m in sorted(keep):
        idx = [i for i, y in enumerate(yte) if y == m]
        lines.append(f"| {m} | {len(idx)} | {sum(pf[i] == m for i in idx) / max(1, len(idx)):.0%} |")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "COMMANDS_ONLY.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
