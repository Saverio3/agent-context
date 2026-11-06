"""Pilot: can a computer tell that an AI model is secretly running on it, from ordinary system signals?
And can a network tell that an AI model is split across several machines (the 'worm' pattern)?

Process part: run AI workloads (llama.cpp serving a small model, normal and disguised) and ordinary
heavy workloads (compression, compiling, video encoding, number crunching, database, hashing, web serving);
sample /proc every 0.5 s; save per-window features to data/detector/process.csv.
Network part: run the same model split across 2 'devices' (llama.cpp RPC) and ordinary network traffic;
capture packets on loopback; save per-window flow features to data/detector/network.csv.
"""
import csv, os, random, shutil, signal, socket, subprocess, sys, threading, time
import numpy as np

B = os.environ.get("LLAMA_BIN", "llama.cpp/build/bin")
MODEL = os.environ.get("MODEL", "model.gguf")
DUR, REPS, DT, WIN = 30, 3, 0.5, 10          # seconds per run, repetitions, sample period, samples per window
os.makedirs("data/detector", exist_ok=True)
PROMPTS = ["Explain how a refrigerator works.", "Write a short story about a lighthouse.",
           "List ten facts about volcanoes.", "Summarise the history of Rome in detail."]


def sh(cmd, **kw):
    return subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)


def kill(p):
    try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except Exception: pass


def wait_port(port, t=120):
    end = time.time() + t
    while time.time() < end:
        try:
            socket.create_connection(("127.0.0.1", port), 1).close(); return True
        except OSError: time.sleep(1)
    return False


def client_loop(port, stop):
    while not stop.is_set():
        subprocess.run(f"curl -s -m 60 http://127.0.0.1:{port}/completion -d '{{\"prompt\": \"{random.choice(PROMPTS)}\", \"n_predict\": 200}}' >/dev/null", shell=True)


def read_proc(pid):
    d = {}
    try:
        st = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
        d["utime"], d["stime"] = int(st[11]), int(st[12])
        d["minflt"], d["majflt"] = int(st[7]), int(st[9])
        d["threads"] = int(st[17])
        for l in open(f"/proc/{pid}/status"):
            k, _, v = l.partition(":")
            if k in ("RssAnon", "RssFile", "RssShmem", "VmRSS", "voluntary_ctxt_switches", "nonvoluntary_ctxt_switches"):
                d[k] = int(v.split()[0])
        for l in open(f"/proc/{pid}/io"):
            k, _, v = l.partition(":")
            if k in ("read_bytes", "write_bytes", "rchar", "wchar"):
                d[k] = int(v)
    except Exception:
        return None
    return d


def tree_pids(root):
    out = subprocess.run(f"pstree -p {root} | grep -o '([0-9]*)' | tr -d '()'", shell=True, capture_output=True, text=True).stdout.split()
    return [int(x) for x in out] or [root]


def sample(root, dur):
    """Sum counters over the process tree every DT seconds; return list of dicts."""
    rows, t0 = [], time.time()
    while time.time() - t0 < dur:
        agg = {}
        for pid in tree_pids(root):
            d = read_proc(pid)
            if d:
                for k, v in d.items(): agg[k] = agg.get(k, 0) + v
        rows.append(agg); time.sleep(DT)
    return rows


def windows(rows, label, kind, rep):
    out, hz = [], os.sysconf("SC_CLK_TCK")
    for s in range(0, len(rows) - WIN, WIN):
        a, b = rows[s], rows[s + WIN]
        if not a or not b: continue
        T = WIN * DT
        g = lambda k: (b.get(k, 0) - a.get(k, 0)) / T
        rss = [r.get("VmRSS", 0) / 1024 for r in rows[s:s + WIN + 1]]
        out.append(dict(kind=kind, label=label, rep=rep,
                        cpu=(g("utime") + g("stime")) / hz, sys_share=g("stime") / max(1e-9, g("utime") + g("stime")),
                        rss_mb=np.mean(rss), rss_cv=np.std(rss) / max(1e-9, np.mean(rss)),
                        file_mb=b.get("RssFile", 0) / 1024, anon_mb=b.get("RssAnon", 0) / 1024,
                        file_share=b.get("RssFile", 0) / max(1, b.get("VmRSS", 1)),
                        minflt=g("minflt"), majflt=g("majflt"), vcs=g("voluntary_ctxt_switches"),
                        nvcs=g("nonvoluntary_ctxt_switches"), rchar=g("rchar") / 1e6, wchar=g("wchar") / 1e6,
                        rdisk=g("read_bytes") / 1e6, wdisk=g("write_bytes") / 1e6, threads=b.get("threads", 0)))
    return out


def ai_server(extra, binary=None):
    exe = f"{B}/llama-server"
    if binary:
        shutil.copy(exe, binary); exe = binary
    return f"{exe} -m {MODEL} --port 8090 -t 2 -c 2048 {extra}"


PROCESS = {
    # label: (is_ai, start-command, needs AI client)
    "ai_server": (1, lambda: ai_server(""), True),
    "ai_disguised": (1, lambda: ai_server("--no-mmap", "/tmp/sysupdated"), True),
    "ai_batch_bench": (1, lambda: f"while true; do {B}/llama-bench -m {MODEL} -t 2 -r 20 -p 256 -n 128; done", False),
    "compress_xz": (0, lambda: "head -c 400M /dev/urandom > /tmp/r.bin; while true; do xz -T2 -6 -c /tmp/r.bin > /dev/null; done", False),
    "compile_gcc": (0, lambda: "python3 -c \"print('\\n'.join(f'int f{i}(int x){{int s=0;for(int j=0;j<x;j++)s+=j*{i}%7;return s;}}' for i in range(30000)))\" > /tmp/big.c; while true; do gcc -O2 -c /tmp/big.c -o /tmp/big.o; done", False),
    "video_ffmpeg": (0, lambda: "while true; do ffmpeg -loglevel quiet -y -f lavfi -i testsrc=size=1280x720:rate=30 -t 20 -threads 2 -c:v libx264 /tmp/o.mp4; done", False),
    "numpy_matmul": (0, lambda: "python3 -c \"import numpy as np\nA=np.random.rand(1500,1500).astype('float32')\nwhile True: A=(A@A); A/=A.max()\"", False),
    "numpy_bigarray": (0, lambda: "python3 -c \"import numpy as np\nX=np.random.rand(60_000_000).astype('float32')\nwhile True: X=np.sort(X)[::-1].copy(); X*=1.0001\"", False),
    "sqlite_db": (0, lambda: "python3 -c \"import sqlite3,random\nc=sqlite3.connect('/tmp/t.db');c.execute('create table if not exists t(a,b)')\nwhile True:\n c.executemany('insert into t values(?,?)',[(random.random(),str(random.random())*5) for _ in range(20000)]);c.commit();c.execute('select avg(a) from t where b like \\'%9%\\'').fetchall()\"", False),
    "hash_sha": (0, lambda: "head -c 1G /dev/urandom > /tmp/h.bin; while true; do sha256sum /tmp/h.bin; done", False),
}


def run_process_part():
    rows = []
    for label, (is_ai, cmd, client) in PROCESS.items():
        for rep in range(REPS):
            p = sh(cmd())
            stop = threading.Event()
            if client:
                if not wait_port(8090):
                    print("server failed", label); kill(p); continue
                th = [threading.Thread(target=client_loop, args=(8090, stop)) for _ in range(2)]
                [t.start() for t in th]
            time.sleep(3)
            data = sample(p.pid, DUR)
            stop.set(); kill(p); time.sleep(2)
            w = windows(data, label, is_ai, rep); rows += w
            print(label, rep, len(w), "windows", flush=True)
    with open("data/detector/process.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)


# ---------------- network part ----------------

def capture(ports, dur):
    flt = " or ".join(f"tcp port {p}" for p in ports)
    cap = subprocess.Popen(f"sudo timeout {dur} tcpdump -i lo -nn -tt -q '{flt}' 2>/dev/null", shell=True, stdout=subprocess.PIPE, text=True)
    out, _ = cap.communicate()
    pk = []
    for l in out.splitlines():
        try:
            t, _, src, _, dst, _, _, n = l.split()[:8]
            pk.append((float(t), int(n), src.rsplit(".", 1)[1], dst.rstrip(":").rsplit(".", 1)[1]))
        except Exception:
            pass
    return pk


def net_windows(pk, label, kind, rep, wsec=5.0):
    if not pk: return []
    t0, rows = pk[0][0], []
    T = int((pk[-1][0] - t0) // wsec)
    for k in range(T):
        sub = [p for p in pk if t0 + k * wsec <= p[0] < t0 + (k + 1) * wsec and p[1] > 0]
        if len(sub) < 5: continue
        bins = np.histogram([p[0] for p in sub], bins=50, range=(t0 + k * wsec, t0 + (k + 1) * wsec), weights=[p[1] for p in sub])[0]
        sizes = np.array([p[1] for p in sub])
        ac = [np.corrcoef(bins[:-l], bins[l:])[0, 1] if bins[:-l].std() > 0 and bins[l:].std() > 0 else 0 for l in range(1, 10)]
        dirs = {}
        for p in sub: dirs[(p[2], p[3])] = dirs.get((p[2], p[3]), 0) + p[1]
        v = sorted(dirs.values(), reverse=True)
        rows.append(dict(kind=kind, label=label, rep=rep, pps=len(sub) / wsec, mbps=sizes.sum() / wsec / 1e6,
                         mean_pkt=sizes.mean(), big_pkt_share=(sizes > 1400).mean(), small_pkt_share=(sizes < 200).mean(),
                         burst_cv=bins.std() / max(1e-9, bins.mean()), idle_share=(bins == 0).mean(),
                         ac_max=max(ac), ac_lag=int(np.argmax(ac)) + 1, n_flows=len(dirs),
                         dir_balance=(v[1] / v[0]) if len(v) > 1 else 0))
    return rows


def run_network_part():
    rows = []
    def ai_split(rep):
        a = sh(f"{B}/rpc-server -p 50052 -t 1"); b = sh(f"{B}/rpc-server -p 50053 -t 1")
        time.sleep(3)
        s = sh(f"{B}/llama-server -m {MODEL} --port 8091 -t 1 -c 2048 -ngl 99 --rpc 127.0.0.1:50052,127.0.0.1:50053")
        ok = wait_port(8091, 300)
        stop = threading.Event(); th = threading.Thread(target=client_loop, args=(8091, stop)); th.start()
        time.sleep(3)
        pk = capture([50052, 50053], DUR)
        stop.set(); [kill(x) for x in (a, b, s)]; time.sleep(2)
        return pk, ok
    def bulk(rep):
        srv = sh("cd /tmp && python3 -m http.server 8201")
        time.sleep(2)
        cl = sh("head -c 300M /dev/urandom > /tmp/f.bin; while true; do curl -s http://127.0.0.1:8201/f.bin -o /dev/null; done")
        pk = capture([8201], DUR); [kill(x) for x in (srv, cl)]; return pk, True
    def chatty(rep):
        code = ("import socket,threading,random,time\n"
                "def srv():\n s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',8202));s.listen()\n"
                " while True:\n  c,_=s.accept()\n  threading.Thread(target=lambda c=c:[c.sendall(c.recv(65536)*random.randint(1,20)) for _ in iter(int,1)],daemon=True).start()\n"
                "threading.Thread(target=srv,daemon=True).start();time.sleep(1)\n"
                "c=socket.create_connection(('127.0.0.1',8202))\n"
                "while True:\n c.sendall(bytes(random.randint(50,4000)));c.recv(1<<20);time.sleep(random.expovariate(30))\n")
        open("/tmp/chatty.py", "w").write(code)
        p = sh("python3 /tmp/chatty.py"); pk = capture([8202], DUR); kill(p); return pk, True
    def stream(rep):
        srv = sh("ffmpeg -loglevel quiet -re -f lavfi -i testsrc=size=1280x720:rate=30 -c:v libx264 -b:v 3M -f mpegts tcp://127.0.0.1:8203?listen")
        time.sleep(2); cl = sh("ffmpeg -loglevel quiet -i tcp://127.0.0.1:8203 -f null -")
        pk = capture([8203], DUR); [kill(x) for x in (srv, cl)]; return pk, True
    def db_sync(rep):
        srv = sh("cd /tmp && python3 -m http.server 8204")
        cl = sh("for i in $(seq 1 100000); do head -c $((RANDOM*20)) /dev/urandom > /tmp/s$i; curl -s http://127.0.0.1:8204/s$i -o /dev/null; rm /tmp/s$i; sleep 0.0$((RANDOM%9)); done")
        pk = capture([8204], DUR); [kill(x) for x in (srv, cl)]; return pk, True
    for label, fn, kind in [("ai_split_rpc", ai_split, 1), ("bulk_download", bulk, 0), ("chatty_api", chatty, 0),
                            ("video_stream", stream, 0), ("small_file_sync", db_sync, 0)]:
        for rep in range(REPS):
            pk, ok = fn(rep)
            w = net_windows(pk, label, kind, rep); rows += w
            print("net", label, rep, ok, len(pk), "packets", len(w), "windows", flush=True)
    with open("data/detector/network.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "both"
    if part in ("process", "both"): run_process_part()
    if part in ("network", "both"): run_network_part()
