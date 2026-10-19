import csv

ROOT = "/mnt/smartssd/wlx/cssys"
V = ["qnn", "qnn_dotp8", "qnn_dotp8u4", "qnn_dotp8x2", "qnn_dotp8x4", "qnn_dotp8x4c"]
COLS = ["insts", "cycles", "squashed_insts", "squash_ratio", "bp_committed",
        "bp_mispredicts", "bp_miss_rate", "l1d_misses", "l1d_mshr_misses",
        "l1d_mlp", "load_to_use"]

hdr = list(csv.DictReader(open("%s/results/lab5_qnn.csv" % ROOT)).fieldnames)
print("COLUMNS:", ",".join(hdr))
print()
for v in V:
    r = list(csv.DictReader(open("%s/results/lab5_%s.csv" % (ROOT, v))))[0]
    out = []
    for c in COLS:
        if c not in r:
            continue
        x = float(r[c])
        out.append("%s=%s" % (c, int(x) if x == int(x) else round(x, 4)))
    print("%-14s %s" % (v, " ".join(out)))

print()
for v in V:
    st = "%s/out/sweeps/lab5_%s/p000/stats.txt" % (ROOT, v)
    n = 0
    got = {}
    for line in open(st):
        if "Begin Simulation Statistics" in line:
            n += 1
        elif n == 2:
            for k in ("system.cpu.fetchStats0.icacheStallCycles",
                      "system.cpu.fetchStats0.numFetchSquashCycles",
                      "system.cpu.fetch.cacheLines",
                      "system.cpu.commit.loads",
                      "system.cpu.numCycles"):
                if line.startswith(k + " ") or line.startswith(k + "\t"):
                    got[k.split(".")[-1]] = int(float(line.split()[1]))
    print("%-14s %s" % (v, " ".join("%s=%d" % kv for kv in sorted(got.items()))))
