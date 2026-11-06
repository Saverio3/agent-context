"""Download mini-SWE-agent v2 runs: same agent, same 500 tasks, 13 different AI models (public S3 bucket).
Writes data/mini.jsonl: {"id": "mini:<model>:<task>", "messages": [[role, text], ...]}"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
import boto3
from botocore import UNSIGNED
from botocore.config import Config

RUNS = """20260217_mini-v2.0.0_claude-4-5-haiku-high 20260217_mini-v2.0.0_claude-4-5-opus-high
20260217_mini-v2.0.0_claude-4-5-sonnet-high 20260217_mini-v2.0.0_claude-4-6-opus 20260217_mini-v2.0.0_deepseek-3-2-high
20260217_mini-v2.0.0_gemini-3-flash-high 20260217_mini-v2.0.0_glm-5-high 20260217_mini-v2.0.0_gpt-5-2-high
20260217_mini-v2.0.0_gpt-5-mini 20260217_mini-v2.0.0_kimi-k2-5-high 20260217_mini-v2.0.0_minimax-2-5-high
20260219_mini-v2.0.0_gpt-5-2-codex 20260226_mini-v2.0.0_gemini-3-pro-high""".split()
s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED, max_pool_connections=32))
B = "swe-bench-submissions"


def text(c):
    if isinstance(c, list):
        return " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return str(c or "")


def get(key):
    try:
        d = json.loads(s3.get_object(Bucket=B, Key=key)["Body"].read())
    except Exception as e:
        return None
    msgs = d.get("messages") or d.get("history") or d.get("trajectory") or []
    return [[m.get("role", ""), text(m.get("content"))] for m in msgs if isinstance(m, dict)]


def main(limit):
    os.makedirs("data", exist_ok=True)
    n = 0
    with open("data/mini.jsonl", "w") as out, ThreadPoolExecutor(24) as ex:
        for run in RUNS:
            model = run.split("_", 2)[2]
            keys = []
            for page in s3.get_paginator("list_objects_v2").paginate(Bucket=B, Prefix=f"verified/{run}/trajs/"):
                keys += [o["Key"] for o in page.get("Contents", []) if o["Key"].endswith((".json", ".traj"))]
            keys = sorted(keys)[:limit]
            got = 0
            for k, msgs in zip(keys, ex.map(get, keys)):
                if msgs:
                    task = os.path.basename(k).rsplit(".", 1)[0].replace(".traj", "")
                    out.write(json.dumps({"id": f"mini:{model}:{task}", "messages": msgs}) + "\n")
                    got += 1
            print(f"{model}: {len(keys)} files, {got} runs", flush=True)
            n += got
    print("total", n)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
