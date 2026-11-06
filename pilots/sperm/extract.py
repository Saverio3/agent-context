"""Download VISEM-Tracking (6.3 GB, Zenodo), list contents, and pack every label/CSV file into a small archive
data/visem/labels.tar.gz so analysis can run without the videos."""
import os, subprocess, tarfile, zipfile, urllib.request, shutil
URL = "https://zenodo.org/records/7293726/files/VISEM-Tracking.zip?download=1"
os.makedirs("data/visem", exist_ok=True)
z = "/tmp/visem.zip"
if not os.path.exists(z):
    subprocess.run(["curl", "-sSL", "--retry", "5", "-o", z, URL], check=True)
print("zip bytes", os.path.getsize(z))
zf = zipfile.ZipFile(z)
names = zf.namelist()
print("entries", len(names))
ext = {}
for n in names:
    e = os.path.splitext(n)[1].lower(); ext[e] = ext.get(e, 0) + 1
print("by extension", ext)
small = [n for n in names if os.path.splitext(n)[1].lower() in (".txt", ".csv", ".xlsx", ".json", ".md", ".yaml", ".yml")]
print("first small files:", small[:40])
with tarfile.open("data/visem/labels.tar.gz", "w:gz") as t:
    for n in small:
        info = zf.getinfo(n)
        if info.file_size > 50_000_000:
            continue
        p = os.path.join("/tmp/visem_small", n)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with zf.open(n) as src, open(p, "wb") as dst:
            shutil.copyfileobj(src, dst)
        t.add(p, arcname=n)
print("packed", os.path.getsize("data/visem/labels.tar.gz"), "bytes")
