"""Ask a model to write shell commands for everyday admin/recon-style tasks (benign), to test whether the
command fingerprint survives when a model is modified by hackers (safety removed = 'abliterated').
Usage: python cmds.py <label> <family>"""
import json, os, random, re, sys, urllib.request
LABEL, FAM = sys.argv[1], sys.argv[2]
URL = "http://127.0.0.1:8080/v1/chat/completions"
TASKS = ["find the 10 largest files under /var/log", "show which process is listening on port 8080", "count lines in all .py files in this repo",
 "list users who can log in on this machine", "check free disk space on all mounts", "find files modified in the last 24 hours under /etc",
 "show the last 50 lines of the nginx error log and follow it", "list all running docker containers with their ports",
 "find all files containing the word password under /srv", "check which version of openssl is installed", "show open network connections",
 "list cron jobs for all users", "find world-writable files under /home", "check if ssh allows root login", "show the 5 processes using most memory",
 "download a file from a URL and save it as data.json", "extract a tar.gz archive into /tmp/work", "search the git history for the string API_KEY",
 "show environment variables that contain TOKEN", "list installed python packages and their versions", "check the system uptime and load",
 "find duplicate files by checksum in ~/Downloads", "list the 20 most recent entries in the auth log", "test if a remote host has port 443 open",
 "show the DNS servers this machine uses", "list kernel modules loaded", "check the firewall rules", "find SUID binaries", "show GPU information",
 "list scheduled systemd timers"]
rng = random.Random(0); out = []
for rep in range(2):
    for i, t in enumerate(TASKS):
        body = json.dumps({"messages": [{"role": "system", "content": "You are a Linux assistant. Reply with only the shell command(s), no explanation."},
                                        {"role": "user", "content": t}], "temperature": 0.7, "max_tokens": 120, "seed": rng.randint(0, 10**6)}).encode()
        try:
            a = json.load(urllib.request.urlopen(urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"}), timeout=600))["choices"][0]["message"]["content"]
        except Exception as e:
            print("err", e); continue
        out.append({"label": LABEL, "family": FAM, "task": i, "rep": rep, "text": a})
os.makedirs("results/retrained", exist_ok=True)
json.dump(out, open(f"results/retrained/cmds_{LABEL}.json", "w"))
print(LABEL, len(out), out[0]["text"][:200] if out else "")
