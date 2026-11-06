"""Pull only the participant CSVs out of the 35 GB visem.zip with HTTP range requests (no full download)."""
import os, sys
from remotezip import RemoteZip
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/visem"
os.makedirs(OUT, exist_ok=True)
for url in ["https://datasets.simula.no/downloads/visem.zip", "https://datasets.simula.no/downloads/visem/visem.zip"]:
    try:
        with RemoteZip(url) as z:
            names = z.namelist()
            print(url, len(names), "members"); print([n for n in names if not n.lower().endswith(".avi")][:40])
            for n in names:
                if n.lower().endswith((".csv", ".txt", ".xlsx")):
                    z.extract(n, OUT); print("got", n)
        break
    except Exception as e:
        print("fail", url, e)
