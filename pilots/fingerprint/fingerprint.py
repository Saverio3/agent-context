"""Pilot: can we tell WHICH AI model ran an agent from its behaviour alone, and predict its next move?

Data: public SWE-agent runs (nebius/SWE-agent-trajectories), each labelled with the model that produced it.
Split by task (same task never in train and test), so the detector must learn the model's habits, not the task.

Part A - fingerprint: features = which commands it uses and in what order, how it opens its messages,
         message lengths, formatting habits. Classifier: logistic regression on these 'style tokens'.
Part B - next move: predict the next command type from the previous two. Compare a generic predictor with
         one specialised to the model the fingerprint guessed from the first half of the run.
"""
import json, re, sys, os, zlib, statistics
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

CODE = re.compile(r"```(?:\w+)?\n(.*?)```", re.S)
WORD = re.compile(r"[A-Za-z_]+")


def actions(msgs):
    out = []
    for role, text in msgs:
        if role not in ("assistant", "ai", "model"):
            continue
        blocks = CODE.findall(text)
        cmd = blocks[-1].strip() if blocks else ""
        verb = "none"
        for seg in re.split(r"&&|\|\||;|\n", cmd):
            w = WORD.findall(seg)
            if w and w[0].lower() not in ("cd", "export", "set", "source"):
                verb = w[0].lower(); break
        out.append((verb, text))
    return out


def tokens(acts):
    t = []
    types = [a for a, _ in acts]
    t += [f"A_{a}" for a in types]
    t += [f"B_{a}_{b}" for a, b in zip(types, types[1:])]
    for _, text in acts:
        pre = text.split("```")[0].strip()
        ws = pre.split()
        if ws:
            op = [w.lower().strip(".,:!") for w in ws[:2]]
            if all(re.fullmatch(r"[a-z']+", w) for w in op):
                t.append("O_" + "_".join(op))
        n = len(pre)
        t.append(f"L_{min(9, n // 150)}")
        if re.search(r"^#+ ", pre, re.M): t.append("F_heading")
        if re.search(r"^\s*[-*] ", pre, re.M): t.append("F_bullets")
        if "**" in pre: t.append("F_bold")
        if re.search(r"[☀-➿\U0001F300-\U0001FAFF]", pre): t.append("F_emoji")
        if "DISCUSSION" in text: t.append("F_discussion_tag")
    t.append(f"N_{min(20, len(acts) // 5)}")
    return " ".join(t)


def main(path, out):
    runs = []
    for line in open(path):
        d = json.loads(line)
        _, model, inst = (d["id"].split(":", 2) + ["", ""])[:3]
        inst = re.sub(r"[^A-Za-z0-9_.-].*$", "", inst) or inst
        acts = actions(d["messages"])
        if len(acts) >= 4 and model and sum(x == "none" for x, _ in acts) <= len(acts) / 2:
            runs.append((model, inst, acts))
    cnt = Counter(m for m, _, _ in runs)
    keep = {m for m, c in cnt.items() if c >= 60}
    runs = [r for r in runs if r[0] in keep]
    test = lambda inst: zlib.crc32(inst.encode()) % 4 == 0
    tr = [r for r in runs if not test(r[1])]
    te = [r for r in runs if test(r[1])]
    labels = sorted(keep)
    lines = [f"# Fingerprinting pilot — {len(runs)} runs, {len(labels)} models (≥60 runs each)", "",
             "Train/test split by task: the same task never appears in both.", ""]

    vec = TfidfVectorizer(token_pattern=r"\S+", ngram_range=(1, 1), min_df=3, sublinear_tf=True)
    Xtr = vec.fit_transform([tokens(a) for _, _, a in tr]); ytr = [m for m, _, _ in tr]
    clf = LogisticRegression(max_iter=3000, C=4.0, class_weight="balanced").fit(Xtr, ytr)

    def score(frac):
        X = vec.transform([tokens(a[: max(2, int(len(a) * frac))]) for _, _, a in te])
        return accuracy_score([m for m, _, _ in te], clf.predict(X))

    chance = max(cnt[m] for m in labels) / sum(cnt[m] for m in labels)
    lines += ["## A. Which model is it?", "",
              "| Evidence seen | Accuracy |", "|---|---|",
              f"| Guessing the most common model (baseline) | {chance:.1%} |",
              f"| First 3 steps only | {accuracy_score([m for m,_,_ in te], clf.predict(vec.transform([tokens(a[:3]) for _,_,a in te]))):.1%} |",
              f"| First 25% of the run | {score(0.25):.1%} |",
              f"| First half of the run | {score(0.5):.1%} |",
              f"| Whole run | {score(1.0):.1%} |", ""]
    pred = clf.predict(vec.transform([tokens(a) for _, _, a in te]))
    per = defaultdict(lambda: [0, 0])
    for (m, _, _), p in zip(te, pred):
        per[m][0] += m == p; per[m][1] += 1
    lines += ["| Model | Test runs | Correctly identified |", "|---|---|---|"]
    lines += [f"| {m} | {n} | {c / n:.0%} |" for m, (c, n) in sorted(per.items(), key=lambda kv: -kv[1][1])]
    feats = np.array(vec.get_feature_names_out())
    lines += ["", "Strongest giveaways per model (top 6 habits):", ""]
    for k, m in enumerate(clf.classes_):
        top = feats[np.argsort(clf.coef_[k])[-6:][::-1]]
        lines.append(f"- **{m}**: " + ", ".join(top))

    # ---- B. next move ----
    def ngram_model(seqs):
        c = defaultdict(Counter)
        for s in seqs:
            s = ["^", "^"] + s
            for a, b, n in zip(s, s[1:], s[2:]):
                c[(a, b)][n] += 1
        return c

    def predict(c, cb, a, b):
        if c.get((a, b)):
            return c[(a, b)].most_common(1)[0][0]
        return cb.most_common(1)[0][0]

    seqs = {m: [[x for x, _ in a] for mm, _, a in tr if mm == m] for m in labels}
    gen = ngram_model([s for v in seqs.values() for s in v])
    per_model = {m: ngram_model(v) for m, v in seqs.items()}
    back = Counter(x for v in seqs.values() for s in v for x in s)
    hit_g = hit_m = hit_o = n = 0
    for m, _, a in te:
        s = [x for x, _ in a]
        half = max(2, len(s) // 2)
        guess = clf.predict(vec.transform([tokens(a[:half])]))[0]
        ss = ["^", "^"] + s
        for i in range(half + 2, len(ss)):
            x, y, nxt = ss[i - 2], ss[i - 1], ss[i]
            hit_g += predict(gen, back, x, y) == nxt
            hit_m += predict(per_model[guess], back, x, y) == nxt
            hit_o += predict(per_model[m], back, x, y) == nxt
            n += 1
    lines += ["", "## B. Can we predict its next move? (second half of each test run)", "",
              "| Predictor | Next command type correct |", "|---|---|",
              f"| Generic (all models pooled) | {hit_g / n:.1%} |",
              f"| Specialised to the model the fingerprint guessed | {hit_m / n:.1%} |",
              f"| Specialised to the true model (upper bound) | {hit_o / n:.1%} |",
              "", f"Predictions scored: {n:,}. Command types: {len(back)} distinct."]
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "FINGERPRINT.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
