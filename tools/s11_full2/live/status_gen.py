"""Build the page's status/now document from the local parts folder, running local renders and machine notes."""
import json, os, re, subprocess, sys, time, datetime
S = os.path.dirname(os.path.abspath(__file__))
H = "/home/user/concert-backdrops/work/s11_full2/" + os.environ.get("S11_TAG", "h8")
CHUNK_S = 270.0                      # typical CPU-limited wall time of one 5 s part here, 4 at once
SEC = json.load(open(f"{S}/sections.json"))       # list with name, span, pass, url, updated, note, c0, c1
M = json.load(open(f"{S}/machines.json"))         # {title, text, machines:[{machine, chunks:[..], started, minutes, what}]}
now = time.time()
done = {int(f[1:3]) for f in os.listdir(H) if re.fullmatch(r"c\d\d\.mp4", f)}
# local renders in progress
local = {}
ps = subprocess.run(["ps", "-eo", "etimes,args"], capture_output=True, text=True).stdout
for line in ps.splitlines():
    m = re.search(r"^\s*(\d+)\s+.*render\.py --range (\d+) (\d+) --out \S*/h[0-9]+/c(\d\d)\.tmp\.mp4", line)
    if m:
        local[int(m.group(4))] = min(0.97, int(m.group(1)) / CHUNK_S)
frac = {c: 1.0 for c in done}
frac.update({c: f for c, f in local.items() if c not in done})
jobs = []
for c, f in sorted(local.items()):
    if c in done: continue
    t0 = c * 5; jobs.append(dict(machine="This machine", what=f"part {c} ({t0 // 60}:{t0 % 60:02d} to {(t0 + 5) // 60}:{(t0 + 5) % 60:02d})", pct=round(100 * f)))
for mc in M.get("machines", []):
    todo = [c for c in mc["chunks"] if c not in done]
    if not todo: continue
    got = len(mc["chunks"]) - len(todo)
    st = datetime.datetime.fromisoformat(mc["started"].replace("Z", "+00:00")).timestamp()
    f = min(0.97, (now - st) / (60.0 * mc["minutes"]))
    for c in todo: frac[c] = max(frac.get(c, 0.0), f)
    jobs.append(dict(machine=mc["machine"], what=mc["what"] + f": {got} of {len(mc['chunks'])} parts in", pct=round(100 * max(f, got / len(mc["chunks"])))))
out = []
for s in SEC:
    cs = range(s["c0"], s["c1"] + 1)
    p = 100.0 if s.get("state") == "ready" else 100.0 * sum(frac.get(c, 0.0) for c in cs) / len(cs)
    d = {k: v for k, v in s.items() if k not in ("c0", "c1")}
    d["pct"] = round(p) if s.get("state") != "ready" else 100
    out.append(d)
ready = sum(1 for s in SEC if s.get("state") == "ready" and s.get("pass") == "grand")
# the machines panel: this machine from its running renders, the cloud machines from machines.json
nloc = sum(1 for c in local if c not in done)
roster = [dict(name="This machine (4 cores)", state="rendering" if nloc else "idle",
               doing=("parts " + ", ".join(str(c) for c in sorted(local) if c not in done)) if nloc else "Waiting for the next order",
               parts=M.get("local_parts", ""), last=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))]
for mc in M.get("roster", []):
    d = dict(mc)
    if d.get("chunks"):
        got = sum(1 for c in d["chunks"] if c in done)
        d["parts"] = f"{got} of {len(d['chunks'])} parts received" + (" (it renders 4 at a time)" if got < len(d["chunks"]) else "")
        if got == len(d["chunks"]) and d.get("state") == "rendering":
            d["state"] = "idle"; d["doing"] = "Finished; next order on the way"
        d.pop("chunks")
    roster.append(d)
doc = dict(updated=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), active=bool(jobs), title=M.get("title", "Render"),
           text=f"{ready} of {len(SEC)} sections ready. " + M.get("text", ""), jobs=jobs, sections=out, machines=roster)
json.dump(doc, open(f"{S}/status.json", "w"), indent=1)
print(json.dumps(dict(jobs=jobs, pct=[d["pct"] for d in out])))
