#!/bin/bash
# 实验二剩余的验证：替换策略家族 / 延迟模型敏感度 / 综合配置交互作用 / 跨负载
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"

# 思考题 3：真实处理器用的替换策略家族
$S --name lab2_replfam --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 64kB --l1d-assoc 4" \
   --vary l1d-repl=lru,random,fifo,nru,rrip,brrip --jobs 6 2>&1 | tail -10
echo REPLFAMDONE

# 思考题 2：结论对延迟模型参数有多敏感
$S --name lab2_latsens --bench qnn --bench-args 8 \
   --base "--cpu o3" \
   --vary l1d-size=8kB,32kB,128kB,256kB --vary l1-latency=2,3,5 --jobs 12 2>&1 | tail -14
echo LATSENSDONE

# 任务 6：单维外推 vs 实测（看参数交互）
$S --name lab2_final --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 128kB --l1d-assoc 4 --cacheline 256 --l2-size 128kB" \
   --vary l1d-repl=lru,random --jobs 2 2>&1 | tail -6
echo FINALDONE

# 任务 6(3)：换负载，提案还成立吗
$S --name lab2_pchase --bench pchase --bench-args "256 200000" \
   --base "--cpu o3" \
   --vary l1d-size=32kB,128kB --vary cacheline=64,256 --jobs 4 2>&1 | tail -8
echo PCHASEDONE
