"""Download VISEM (85 men: videos + csvs) from the Hugging Face mirror sperm-net/VISEM.
Lists the repo, prints the structure, downloads csvs and videos (videos one by one, to keep disk low
we let hormones.py read them afterwards; total size printed first)."""
import os
import sys

from huggingface_hub import HfApi, hf_hub_download

REPO = "sperm-net/VISEM"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/visem"
api = HfApi()
info = api.dataset_info(REPO, files_metadata=True)
files = [(s.rfilename, s.size or 0) for s in info.siblings]
print("files:", len(files), "total GB:", round(sum(s for _, s in files) / 1e9, 2))
for f, s in files[:60]:
    print(f, round(s / 1e6, 1), "MB")
want = [f for f, _ in files if f.lower().endswith((".csv", ".avi", ".mp4", ".xlsx", ".txt"))]
for f in want:
    hf_hub_download(REPO, f, repo_type="dataset", local_dir=OUT)
print("downloaded", len(want))
