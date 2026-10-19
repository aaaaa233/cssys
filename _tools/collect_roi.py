"""启动段 / ROI / 收尾段的三段对比（实验一任务 2 的参考数据）。

现在三段来自同一次运行、同一个二进制，不再需要跟 _noroi 版本相减。
"""
import os
import sys

ROOT = "/mnt/smartssd/wlx/cssys"
sys.path.insert(0, os.path.join(ROOT, "framework"))
import stats  # noqa: E402

NAMES = {0: "启动段", 1: "ROI ", 2: "收尾段"}


def show(run, label):
    path = os.path.join(ROOT, "out", "lab1", run, "stats.txt")
    blocks = [stats.summarize(b) for b in stats.parse_blocks(path)]
    ti = sum(b["insts"] for b in blocks)
    tc = sum(b["cycles"] for b in blocks)
    print(f"--- {label}   全程序 {int(ti)} 条指令 / {int(tc)} 周期 "
          f"/ IPC {ti / tc:.3f}")
    print(f"{'段':>8} {'指令数':>12} {'占比':>7} {'周期数':>12} {'占比':>7} "
          f"{'IPC':>7} {'L1D失效率':>10} {'MSHR MPKI':>10}")
    for i, b in enumerate(blocks):
        print(f"{NAMES.get(i, i):>8} {int(b['insts']):>12} "
              f"{b['insts'] / ti:>6.1%} {int(b['cycles']):>12} "
              f"{b['cycles'] / tc:>6.1%} {b['ipc']:>7.3f} "
              f"{b['l1d_miss_rate']:>9.2%} {b['l1d_mshr_mpki']:>10.3f}")
    print()
    return blocks


for n in (8, 64):
    show(f"roi_{n}", f"qnn {n}")

# 对照：不带标记的版本，整个程序只有一段
for n in (8, 64):
    path = os.path.join(ROOT, "out", "lab1", f"noroi_{n}", "stats.txt")
    b = stats.summarize(stats.parse_blocks(path)[0])
    print(f"qnn_noroi {n:>3}: 全程序 {int(b['insts'])} 条 / "
          f"{int(b['cycles'])} 周期 / IPC {b['ipc']:.3f} "
          f"/ L1D失效率 {b['l1d_miss_rate']:.2%}")
