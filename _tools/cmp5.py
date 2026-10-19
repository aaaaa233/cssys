import csv, os

ROOT = "/mnt/smartssd/wlx/cssys"

MAIN = ["qnn", "qnn_dotp8", "qnn_dotp8u4", "qnn_dotp8x2",
        "qnn_dotp8x4", "qnn_dotp8x4c"]
COLS = ["insts", "cycles", "ipc", "l1d_mshr_misses", "fetch_cache_lines",
        "icache_stall_cycles", "l1d_misses", "l1d_mlp", "rob_full_events",
        "iq_full_events", "lq_full_events", "bp_mispredicts", "squash_ratio"]


def load(name):
    p = "%s/results/%s.csv" % (ROOT, name)
    if not os.path.exists(p):
        return None
    return list(csv.DictReader(open(p)))


def fmt(x):
    f = float(x)
    return str(int(f)) if f == int(f) else "%.4f" % f


print("=" * 78)
print("MAIN TABLE   old(03:41) -> new(now)     '*' = changed")
print("=" * 78)
for v in MAIN:
    old, new = load("lab5_" + v), load("lab5b_" + v)
    if not old or not new:
        print("%-14s MISSING" % v)
        continue
    o, n = old[0], new[0]
    print("--- %s ---" % v)
    for c in COLS:
        if c not in o or c not in n:
            continue
        a, b = fmt(o[c]), fmt(n[c])
        mark = " " if a == b else "*"
        delta = ""
        if a != b and float(o[c]) != 0:
            delta = "  (%+.3f%%)" % ((float(n[c]) / float(o[c]) - 1) * 100)
        print("  %s %-22s %14s -> %-14s%s" % (mark, c, a, b, delta))

print()
print("=" * 78)
print("LATENCY SWEEP  old -> new")
print("=" * 78)
for v in ["qnn_dotp8", "qnn_dotp8x2", "qnn_dotp8x4c"]:
    old, new = load("lab5_lat_" + v), load("lab5b_lat_" + v)
    if not old or not new:
        print("%-14s MISSING" % v)
        continue
    print("--- %s ---" % v)
    om = {r["dotp8-lat"]: r for r in old}
    nm = {r["dotp8-lat"]: r for r in new}
    for lat in ["1", "2", "3", "4", "6", "8"]:
        if lat not in om or lat not in nm:
            continue
        a, b = fmt(om[lat]["cycles"]), fmt(nm[lat]["cycles"])
        mark = " " if a == b else "*"
        print("  %s lat=%-3s %12s -> %-12s" % (mark, lat, a, b))
print("CMPDONE")
