#!/bin/bash
# 实验三前置探测
#  (1) MRU 在实验二的病态配置下能不能打败 random —— 决定"一个字符的改动"这个任务成不成立
#  (2) 预取器在 qnn（纯顺序扫描）上的收益 —— 决定任务 4/5 成不成立
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

# (1) 病态配置：64kB / 4 路，工作集 98KB
$S --name lab3_probe_repl --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 64kB --l1d-assoc 4" \
   --vary l1d-repl=lru,random,mru,fifo,lip,bip,secondchance,treeplru --jobs 8 2>&1 | tail -3
$R results/lab3_probe_repl.csv cycles ipc l1d_mshr_mpki l1d_miss_rate
echo REPLDONE

# (2) 预取器：基线 32kB
$S --name lab3_probe_pf --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary l1d-pf=none,tagged,stride,bop,ampm --jobs 5 2>&1 | tail -3
$R results/lab3_probe_pf.csv cycles ipc l1d_mshr_mpki l1d_mlp dram_bytes
echo PFDONE

# 预取器的统计名是什么
grep -oE '^system\.cpu\.dcache\.prefetcher[a-zA-Z0-9_.:]*' \
     out/sweeps/lab3_probe_pf/p002_l1d-pf-stride/stats.txt | sort -u
echo PFSTATDONE
