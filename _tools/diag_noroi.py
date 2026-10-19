"""诊断：qnn 与 qnn_noroi 指令数几乎相同，为什么周期数差 3 倍。"""
import os
import subprocess
import sys

ROOT = "/mnt/smartssd/wlx/cssys"
sys.path.insert(0, os.path.join(ROOT, "framework"))
import stats  # noqa: E402

KEYS = ["insts", "cycles", "ipc",
        "l1i_miss_rate", "l1i_mshr_mpki",
        "l1d_miss_rate", "l1d_mshr_mpki", "l1d_mlp",
        "l2_accesses", "l2_miss_rate", "l2_mshr_mpki",
        "dram_bytes", "dram_read_bytes",
        "bp_miss_rate", "bp_mpki"]

roi_blocks = [stats.summarize(b) for b in
              stats.parse_blocks(os.path.join(ROOT, "out/lab1/roi_8/stats.txt"))]
noroi = stats.summarize(stats.parse_blocks(
    os.path.join(ROOT, "out/lab1/noroi_8/stats.txt"))[0])

agg = {}
for k in KEYS:
    if k in ("insts", "cycles", "l2_accesses", "dram_bytes", "dram_read_bytes"):
        agg[k] = sum(b[k] for b in roi_blocks)
    else:
        agg[k] = float("nan")
agg["ipc"] = agg["insts"] / agg["cycles"]

print(f"{'指标':>18} {'qnn(三段合计)':>16} {'qnn_noroi(全程序)':>18} {'比值':>8}")
for k in KEYS:
    a, b = agg[k], noroi[k]
    ratio = (b / a) if (a == a and a) else float("nan")
    av = f"{a:.4g}" if a == a else "-"
    print(f"{k:>18} {av:>16} {b:>18.4g} {ratio:>8.2f}")

print("\n分段明细（qnn）:")
for i, b in enumerate(roi_blocks):
    print(f"  段{i}: insts={int(b['insts']):>9} cycles={int(b['cycles']):>9} "
          f"ipc={b['ipc']:.3f} l1d_miss={b['l1d_miss_rate']:.2%} "
          f"l1i_miss={b['l1i_miss_rate']:.2%} l2_acc={int(b['l2_accesses'])} "
          f"dram={int(b['dram_bytes'])}")

print("\n关键静态符号地址:")
for exe in ("qnn", "qnn_noroi"):
    out = subprocess.run(
        ["riscv64-linux-gnu-nm", os.path.join(ROOT, "bench/bin/riscv", exe)],
        capture_output=True, text=True).stdout
    syms = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] in ("w1", "w2", "xbuf", "hbuf", "b1",
                                            "b2", "ybuf", "dot_i8", "main"):
            syms[parts[2]] = parts[0]
    print(f"  {exe:>10}: " + "  ".join(f"{k}={v}" for k, v in sorted(syms.items())))
