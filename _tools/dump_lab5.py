import csv, os, subprocess

ROOT = "/mnt/smartssd/wlx/cssys"
V = ["qnn", "qnn_dotp8", "qnn_dotp8u4", "qnn_dotp8x2", "qnn_dotp8x4", "qnn_dotp8x4c"]
LOOP = {"qnn": 0, "qnn_dotp8": 18, "qnn_dotp8u4": 66,
        "qnn_dotp8x2": 38, "qnn_dotp8x4": 66, "qnn_dotp8x4c": 60}


def roi_stat(path, key):
    n = 0
    with open(path) as fh:
        for line in fh:
            if "Begin Simulation Statistics" in line:
                n += 1
            elif n == 2 and line.startswith(key):
                return int(float(line.split()[1]))
    return None


rows = []
for v in V:
    with open("%s/results/lab5_%s.csv" % (ROOT, v)) as fh:
        r = list(csv.DictReader(fh))[0]
    st = "%s/out/sweeps/lab5_%s/p000/stats.txt" % (ROOT, v)
    rows.append((v, int(float(r["insts"])), int(float(r["cycles"])),
                 float(r["ipc"]), int(float(r["l1d_mshr_misses"])),
                 roi_stat(st, "system.cpu.fetchStats0.icacheStallCycles"),
                 roi_stat(st, "system.cpu.fetchStats0.fetchRate") if False else None))

base_i, base_c = rows[0][1], rows[0][2]
print("%-14s %6s %10s %10s %7s %7s %6s %9s %8s" %
      ("版本", "循环B", "指令数", "周期数", "指令比", "加速比", "IPC", "mshr", "取指停顿"))
for v, i, c, ipc, mshr, ic, _ in rows:
    print("%-14s %6d %10d %10d %7.2f %7.2f %6.3f %9d %8d" %
          (v, LOOP[v], i, c, base_i / i, base_c / c, ipc, mshr, ic))
