import csv

ROOT = "/mnt/smartssd/wlx/cssys"
ORDER = ["qnn", "qnn_dotp8", "qnn_dotp8u4", "qnn_dotp8x2",
         "qnn_dotp8x4", "qnn_dotp8x4c"]
BODY = {"qnn": "7 cond/22 B", "qnn_dotp8": "7 cond/18 B", "qnn_dotp8u4": "66 B",
        "qnn_dotp8x2": "38 B", "qnn_dotp8x4": "66 B", "qnn_dotp8x4c": "60 B"}

d = {}
for v in ORDER:
    d[v] = list(csv.DictReader(open("%s/results/lab5b_%s.csv" % (ROOT, v))))[0]


def i(v, c):
    return int(float(d[v][c]))


base_i, base_c = i("qnn", "insts"), i("qnn", "cycles")

print("MAIN TABLE")
for v in ORDER:
    ins, cyc = i(v, "insts"), i(v, "cycles")
    print("| `%s` | %s | %s | %s | %.2f | %.2f | %.3f | %s | %s | %s |" % (
        v, BODY[v], format(ins, ","), format(cyc, ","),
        base_i / ins, base_c / cyc, ins / cyc,
        format(i(v, "l1d_mshr_misses"), ","),
        format(i(v, "fetch_cache_lines"), ","),
        format(i(v, "icache_stall_cycles"), ",")))

print()
print("SUPPLEMENT")
for v in ORDER:
    print("| `%s` | %s | %s | %s | %s | %.4f | %s | %.3f |" % (
        v, format(i(v, "rob_full_events"), ","),
        format(i(v, "iq_full_events"), ","),
        format(i(v, "lq_full_events"), ","),
        format(i(v, "bp_mispredicts"), ","),
        float(d[v]["squash_ratio"]),
        format(i(v, "l1d_misses"), ","), float(d[v]["l1d_mlp"])))

print()
print("LATENCY")
lat = {}
for v in ["qnn_dotp8", "qnn_dotp8x2", "qnn_dotp8x4c"]:
    rows = list(csv.DictReader(open("%s/results/lab5b_lat_%s.csv" % (ROOT, v))))
    lat[v] = {r["dotp8-lat"]: int(float(r["cycles"])) for r in rows}
for L in ["1", "2", "3", "4", "6", "8"]:
    print("| %s | %s | %s | %s |" % (
        L, format(lat["qnn_dotp8"][L], ","),
        format(lat["qnn_dotp8x2"][L], ","),
        format(lat["qnn_dotp8x4c"][L], ",")))

print()
print("DERIVED")
u4, x4, x4c, x1, x2 = (i("qnn_dotp8u4", "cycles"), i("qnn_dotp8x4", "cycles"),
                       i("qnn_dotp8x4c", "cycles"), i("qnn_dotp8", "cycles"),
                       i("qnn_dotp8x2", "cycles"))
iu4, ix4, ix4c = (i("qnn_dotp8u4", "insts"), i("qnn_dotp8x4", "insts"),
                  i("qnn_dotp8x4c", "insts"))
print("u4 vs x4 : insts %+.2f%%  cycles %+.2f%%" % (
    (iu4 / ix4 - 1) * 100, (u4 / x4 - 1) * 100))
print("x4c vs x4: insts %+.2f%%  cycles %+.2f%%" % (
    (ix4c / ix4 - 1) * 100, (x4c / x4 - 1) * 100))
print("x1->x2   : %+.2f%%" % ((x2 / x1 - 1) * 100))
print("x2->x4c  : %+.2f%%" % ((x4c / x2 - 1) * 100))
print("bound x1 304,896/%d = %.2f%%" % (x1, 304896.0 / x1 * 100))
print("bound x2 152,448/%d = %.2f%%" % (x2, 152448.0 / x2 * 100))
print("bound x4c 76,224/%d = %.2f%%" % (x4c, 76224.0 / x4c * 100))
print("TABDONE")
