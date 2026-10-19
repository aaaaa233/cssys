"""教师侧：把 out/lab1/ 下面几个单点运行的统计汇总成一张表。"""
import os
import sys

ROOT = "/mnt/smartssd/wlx/cssys"
sys.path.insert(0, os.path.join(ROOT, "framework"))
import stats  # noqa: E402

RUNS = ["scale_2", "scale_4", "scale_8", "scale_16", "scale_32", "roi", "noroi"]

print(f"{'run':>10} {'blk':>3} {'insts':>12} {'cycles':>12} {'ipc':>7} "
      f"{'sim_s':>10} {'host_s':>8} {'KIPS':>9}")
for name in RUNS:
    path = os.path.join(ROOT, "out", "lab1", name, "stats.txt")
    for blk in (0, 1):
        try:
            s = stats.summarize_file(path, blk)
        except Exception as exc:  # noqa: BLE001
            print(f"{name:>10} {blk:>3}  -- {exc}")
            continue
        if not s.get("insts"):
            continue
        print(f"{name:>10} {blk:>3} {int(s['insts']):>12} {int(s['cycles']):>12} "
              f"{s['ipc']:>7.3f} {s['sim_seconds']:>10.6f} "
              f"{s['host_seconds']:>8.1f} {s['host_inst_rate']/1000:>9.1f}")
