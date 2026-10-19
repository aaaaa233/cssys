#!/bin/bash
# 实验四前置探测：branchy 三个模式的规模与分支可预测性
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"

# branchy 规模探测：n=4096 iters=100，看指令数和主机耗时是否可接受
$S --name lab4_probe --bench branchy --bench-args "0 4096 100" \
   --base "--cpu o3" --vary bp=local,tournament --jobs 2 2>&1 | tail -6
echo PROBEDONE

python3 framework/report.py results/lab4_probe.csv \
    insts cycles ipc bp_lookups bp_miss_rate squash_ratio host_seconds
echo REPORTDONE
