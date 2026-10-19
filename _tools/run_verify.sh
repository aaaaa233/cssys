#!/bin/bash
# 验证两个待解释的现象：
#  A) 64kB 下直接映射为什么反而比 2/4/8 路快 —— 是不是 LRU 在流式访问下的病态行为
#  B) 128kB 拐点两侧的细粒度形状
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"

$S --name lab2_repl --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 64kB" \
   --vary l1d-assoc=1,2,4,8 --vary l1d-repl=lru,random \
   --jobs 8 2>&1 | tail -20
echo REPLDONE

$S --name lab2_knee --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-assoc 2" \
   --vary l1d-size=64kB,80kB,96kB,112kB,128kB \
   --jobs 5 2>&1 | tail -12
echo KNEEDONE

# 关掉自动延迟：演示"越大越好"的假结论
$S --name lab2_nolat --bench qnn --bench-args 8 \
   --base "--cpu o3 --auto-latency off" \
   --vary l1d-size=8kB,16kB,32kB,64kB,128kB,256kB \
   --jobs 6 2>&1 | tail -12
echo NOLATDONE
