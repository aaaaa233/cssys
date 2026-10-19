#!/bin/bash
# 实验三任务 1 的完整参考数据：病态配置下所有现成替换策略
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

$S --name lab3_all_repl --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 64kB --l1d-assoc 4" \
   --vary l1d-repl=lru,fifo,secondchance,treeplru,lfu,random,mru,lip,bip,rrip,brrip,nru,drrip,ship \
   --jobs 8 2>&1 | tail -3
$R results/lab3_all_repl.csv cycles ipc l1d_misses l1d_mshr_misses l1d_mshr_mpki
echo ALLDONE

# 对照：把病态消掉（容量够 / 相联度够），看策略之间还有没有差别
$S --name lab3_nopath --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 128kB --l1d-assoc 4" \
   --vary l1d-repl=lru,random,mru,bip --jobs 4 2>&1 | tail -3
$R results/lab3_nopath.csv cycles ipc l1d_mshr_misses l1d_mshr_mpki
echo NOPATHDONE

# 对照：同样 64kB，但相联度拉到 16，看 LRU 的病态是否随 N/A 比值变化
$S --name lab3_assoc --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 64kB" \
   --vary l1d-assoc=2,4,8,16 --vary l1d-repl=lru,mru --jobs 8 2>&1 | tail -3
$R results/lab3_assoc.csv cycles ipc l1d_mshr_misses l1d_mshr_mpki
echo ASSOCDONE
