"""Download a GGUF: direct URL, or the Q4_K_M (else smallest) file from a Hugging Face repo."""
import sys, urllib.request
from huggingface_hub import HfApi, hf_hub_download
src = sys.argv[1]
if src.startswith("http"):
    urllib.request.urlretrieve(src, "model.gguf")
else:
    fs = [s for s in HfApi().model_info(src, files_metadata=True).siblings if s.rfilename.endswith(".gguf")]
    pick = next((s for s in fs if "q4_k_m" in s.rfilename.lower()), None) or min(fs, key=lambda s: s.size or 1e18)
    print("using", pick.rfilename)
    import shutil; shutil.copy(hf_hub_download(src, pick.rfilename, local_dir="/tmp/m"), "model.gguf")
