"""Download public agent runs from Hugging Face and normalise to data/<name>.jsonl.
Runs inside GitHub Actions (this needs internet access to huggingface.co).

Each output line: {"id": str, "messages": [[role, text], ...]}
"""
import argparse
import json
import os
import random

from huggingface_hub import HfApi, hf_hub_download
import pyarrow.parquet as pq

DATASETS = {
    # SWE-agent runs by many models on SWE-bench-style tasks
    "nebius": ("nebius/SWE-agent-trajectories", "trajectory"),
    # OpenHands runs (different agent, different file-viewing style)
    "swegym": ("SWE-Gym/OpenHands-Sampled-Trajectories", "messages"),
}


def _text(m):
    for k in ("text", "content", "value", "system_prompt"):
        v = m.get(k)
        if v:
            if isinstance(v, list):
                v = " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in v)
            return str(v)
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", choices=DATASETS)
    ap.add_argument("--n", type=int, default=3000)
    a = ap.parse_args()
    repo, col = DATASETS[a.name]
    files = [f for f in HfApi().list_repo_files(repo, repo_type="dataset") if f.endswith(".parquet")]
    random.Random(0).shuffle(files)
    os.makedirs("data", exist_ok=True)
    n = 0
    with open(f"data/{a.name}.jsonl", "w") as out:
        for f in files:
            t = pq.read_table(hf_hub_download(repo, f, repo_type="dataset"))
            cols = [c for c in (col, "instance_id", "model_name", "target", "generated_patch", "patch") if c in t.column_names]
            for i, row in enumerate(t.select(cols).to_pylist()):
                msgs = row.get(col) or []
                if isinstance(msgs, str):
                    msgs = json.loads(msgs)
                norm = [[m.get("role") or m.get("from") or "", _text(m)] for m in msgs if isinstance(m, dict)]
                rid = f"{a.name}:{row.get('model_name', '')}:{row.get('instance_id', f'{f}#{i}')}"
                patch = row.get("generated_patch") or row.get("patch") or ""
                out.write(json.dumps({"id": rid, "solved": row.get("target"), "patch": patch, "messages": norm}) + "\n")
                n += 1
                if n >= a.n:
                    print(f"wrote {n} runs from {repo}")
                    return
    print(f"wrote {n} runs from {repo}")


if __name__ == "__main__":
    main()
