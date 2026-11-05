"""Learned keep/hide predictor for lines of old tool outputs, with a calibrated miss target.

Train:  python -m lab.predict --jsonl data/nebius.jsonl data/swegym.jsonl
Writes lab/model.json (weights + thresholds). Runs whose id hashes even are used for training;
lab.run --test-half scores only the odd ones, so the predictor is always tested on unseen runs.

Label for a line: will any name/path/number in it be written by the agent later in the run?
Threshold: lowest score that still keeps >= (1 - target) of the token-weighted positive lines,
so the expected miss rate is close to the target on new runs.
"""
import argparse
import json
import math
import re
import zlib

import numpy as np

from .core import load_jsonl, salient, toks

KEEP = 3
ERR = re.compile(r"Error|Exception|Traceback|FAIL|failed|assert|Warning|warning|error:", re.I)
PASS = re.compile(r"\b(passed|PASSED|OK|success)\b")
FEATS = ["bias", "len", "n_sal", "echo", "n_echo", "head", "tail", "relpos", "err", "pass",
         "diffline", "numbered", "path", "out_len", "is_file", "is_search", "is_cmd_short"]


def is_train(rid):
    return zlib.crc32(rid.encode()) % 2 == 0


def line_features(lines, echoed, out_text):
    n = len(lines)
    out_len = math.log1p(len(out_text))
    is_file = 1.0 if ("lines total" in out_text or "cat -n" in out_text) else 0.0
    is_search = 1.0 if re.search(r"Found \d+ match|No matches|grep", out_text[:300]) else 0.0
    short = 1.0 if n < 15 else 0.0
    X = np.zeros((n, len(FEATS)))
    for i, l in enumerate(lines):
        sal = salient(l)
        e = sal & echoed
        X[i] = [1, math.log1p(len(l)), math.log1p(len(sal)), 1.0 if e else 0.0, math.log1p(len(e)),
                1.0 if i < 3 else 0.0, 1.0 if i >= n - 3 else 0.0, i / max(1, n - 1),
                1.0 if ERR.search(l) else 0.0, 1.0 if PASS.search(l) else 0.0,
                1.0 if l[:1] in "+-@" else 0.0, 1.0 if re.match(r"\s*\d+[:|]", l) else 0.0,
                1.0 if re.search(r"[\w-]+/[\w./-]+", l) else 0.0, out_len, is_file, is_search, short]
    return X


def examples(ms):
    """Yield (X, y, w) for each tool output at the moment it turns old (KEEP agent steps later)."""
    asst = [i for i, (r, _) in enumerate(ms) if r == "assistant"]
    for i, (r, c) in enumerate(ms):
        if r != "tool":
            continue
        later = [a for a in asst if a > i]
        if len(later) <= KEEP:
            continue
        t = later[KEEP]
        echoed = set()
        for rr, cc in ms[:t]:
            if rr in ("assistant", "task"):
                echoed |= salient(cc)
        future = set()
        for rr, cc in ms[t:]:
            if rr == "assistant":
                future |= salient(cc)
        lines = c.splitlines()
        if not lines:
            continue
        X = line_features(lines, echoed, c)
        y = np.array([1.0 if salient(l) & future else 0.0 for l in lines])
        w = np.array([toks(l) for l in lines], dtype=float)
        yield X, y, w


def fit_logistic(X, y, w, iters=300, lr=0.5, l2=1e-3):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    mu[0], sd[0] = 0, 1
    Z = (X - mu) / sd
    beta = np.zeros(X.shape[1])
    ww = w / w.sum()
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Z @ beta))
        g = Z.T @ (ww * (p - y)) + l2 * beta
        beta -= lr * g
    return beta, mu, sd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", nargs="+")
    ap.add_argument("--limit", type=int, default=1500)
    ap.add_argument("--out", default="lab/model.json")
    a = ap.parse_args()
    Xs, ys, ws = [], [], []
    for path in a.jsonl:
        for rid, ms in load_jsonl(path, a.limit):
            if not is_train(rid):
                continue
            for X, y, w in examples(ms):
                Xs.append(X); ys.append(y); ws.append(w)
    X, y, w = np.vstack(Xs), np.concatenate(ys), np.concatenate(ws)
    beta, mu, sd = fit_logistic(X, y, w)
    s = ((X - mu) / sd) @ beta
    pos = y == 1
    order = np.argsort(s[pos])
    cw = np.cumsum(w[pos][order]) / w[pos].sum()
    thr = {}
    for target in (0.01, 0.03):
        k = np.searchsorted(cw, target)
        thr[str(target)] = float(s[pos][order][min(k, len(order) - 1)])
    keep_share = {t: float(w[s >= v].sum() / w.sum()) for t, v in thr.items()}
    json.dump({"features": FEATS, "beta": beta.tolist(), "mu": mu.tolist(), "sd": sd.tolist(),
               "thresholds": thr, "train_lines": int(len(y)), "positive_share": float((w * y).sum() / w.sum()),
               "kept_token_share": keep_share,
               "weights": dict(zip(FEATS, [round(b, 3) for b in beta.tolist()]))},
              open(a.out, "w"), indent=1)
    print(open(a.out).read())


if __name__ == "__main__":
    main()
