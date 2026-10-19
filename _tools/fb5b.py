import csv

ROOT = "/mnt/smartssd/wlx/cssys"
COLS = ["fetch-buffer", "cycles", "insts", "fetch_cache_lines",
        "icache_stall_cycles", "lq_full_events", "iq_full_events",
        "l1d_mshr_misses", "ipc"]

for v in ["qnn_dotp8x4", "qnn_dotp8x4c"]:
    print("--- %s ---" % v)
    for r in csv.DictReader(open("%s/results/lab5_fb_%s.csv" % (ROOT, v))):
        out = []
        for c in COLS:
            if c not in r:
                continue
            x = float(r[c])
            out.append("%s=%s" % (c, int(x) if x == int(x) else round(x, 4)))
        print("  " + " ".join(out))
print("EXACTDONE")
