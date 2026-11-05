"""Learned predictor with a calibrated 3% miss target (needs lab/model.json from lab.predict)."""
import json
import os

import numpy as np

from ..core import STUB, salient
from .. import predict
from . import m02_collapse

NAME = "Learned keep/hide, 3% miss target (new)"
LOSSLESS = False
DESCRIPTION = ("Version collapse, then each line of a tool output, once it is 3 steps old, is scored by a model "
               "trained on other runs: 'will the agent need this later?'. Lines below a threshold set for a 3% "
               "miss target are stored, not shown. Error/pass lines are always kept.")
TARGET = "0.03"
_M = None
_cache = {}


def _model():
    global _M
    if _M is None:
        p = os.path.join(os.path.dirname(predict.__file__), "model.json")
        _M = json.load(open(p)) if os.path.exists(p) else False
    return _M


def policy(ctx):
    M = _model()
    base = m02_collapse.policy(ctx)
    if not M:
        return base
    beta, mu, sd = np.array(M["beta"]), np.array(M["mu"]), np.array(M["sd"])
    thr = M["thresholds"][TARGET]
    asst = [i for i, (r, _) in enumerate(ctx) if r == "assistant"]
    cutoff = asst[-predict.KEEP] if len(asst) >= predict.KEEP else -1
    if len(ctx) < _cache.get("_len", 0):
        _cache.clear()
    _cache["_len"] = len(ctx)
    echoed = None
    out = []
    for i, (v, (r, c)) in enumerate(zip(base, ctx)):
        if r != "tool" or i >= cutoff or v is not c:
            out.append(v); continue
        key = (TARGET, id(c), i)
        if key not in _cache:
            if echoed is None:
                echoed = set()
                for rr, cc in ctx:
                    if rr in ("assistant", "task"):
                        echoed |= salient(cc)
            lines = c.splitlines()
            if not lines:
                _cache[key] = c
            else:
                s = ((predict.line_features(lines, echoed, c) - mu) / sd) @ beta
                kept = [l for l, sc in zip(lines, s) if sc >= thr or predict.ERR.search(l) or predict.PASS.search(l)]
                _cache[key] = c if len(kept) == len(lines) else (
                    STUB if not kept else "\n".join(kept + [f"[{len(lines) - len(kept)} lines stored]"]))
        out.append(_cache[key])
    return out
