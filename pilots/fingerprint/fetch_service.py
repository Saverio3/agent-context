"""Download trajectories: tau-bench (all), AgentRewardBench (cleaned runs for chosen benchmarks; files are big
because they include page snapshots, so each is reduced to its 'action' strings right after download)."""
import json
import os
import sys

from huggingface_hub import HfApi, hf_hub_download

MODE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
api = HfApi()
if MODE == "tools":
    for s in api.dataset_info("AgentSuite/tau-bench-trajectories").siblings:
        if s.rfilename.endswith(".jsonl"):
            hf_hub_download("AgentSuite/tau-bench-trajectories", s.rfilename, repo_type="dataset", local_dir=OUT)
else:
    def acts(o, out):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "action" and isinstance(v, str):
                    out.append(v)
                else:
                    acts(v, out)
        elif isinstance(o, list):
            for v in o:
                acts(v, out)
        return out
    keep = ("cleaned/webarena/", "cleaned/workarena/", "cleaned/assistantbench/", "cleaned/visualwebarena/")
    files = [s.rfilename for s in api.dataset_info("McGill-NLP/agent-reward-bench").siblings
             if s.rfilename.startswith(keep) and s.rfilename.endswith(".json")]
    print("files", len(files), flush=True)
    first = True
    for i, f in enumerate(files):
        p = hf_hub_download("McGill-NLP/agent-reward-bench", f, repo_type="dataset", local_dir="/tmp/arb_raw")
        try:
            d = json.load(open(p))
            if first:
                print("top keys:", list(d)[:20] if isinstance(d, dict) else type(d)); first = False
            a = acts(d, [])
            dst = os.path.join(OUT, f.replace("cleaned/", ""))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            json.dump({"action": a} if False else [{"action": x} for x in a], open(dst, "w"))
        except Exception as e:
            print("skip", f, e)
        os.remove(p)
        if i % 100 == 0:
            print(i, flush=True)
