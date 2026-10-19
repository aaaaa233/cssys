import csv, sys

ROOT = "/mnt/smartssd/wlx/cssys"
V = ["qnn", "qnn_dotp8", "qnn_dotp8u4", "qnn_dotp8x2", "qnn_dotp8x4", "qnn_dotp8x4c"]

COLS = ["insts", "cycles", "ipc", "l1d_mshr_misses", "l1d_misses", "l1d_mlp",
        "rob_full_events", "iq_full_events", "lq_full_events", "squash_ratio"]

print("=== MAIN (exact) ===")
for v in V:
    r = list(csv.DictReader(open("%s/results/lab5_%s.csv" % (ROOT, v))))[0]
    out = []
    for c in COLS:
        x = float(r[c])
        out.append("%s=%d" % (c, x) if x == int(x) else "%s=%.4f" % (c, x))
    print(v, " ".join(out))

print("=== LAT (exact) ===")
for v in ["qnn_dotp8", "qnn_dotp8x2", "qnn_dotp8x4c"]:
    for r in csv.DictReader(open("%s/results/lab5_lat_%s.csv" % (ROOT, v))):
        print("%-14s lat=%-2s cycles=%d insts=%d ipc=%.3f" %
              (v, r["dotp8-lat"], float(r["cycles"]), float(r["insts"]),
               float(r["ipc"])))
