#!/bin/bash
# 实验四补测 C：
#  (1) 把 branchy mode2 的宽度阶梯加密（1,2,3,4,6,8），确认 4/7→5/7→6/7 是台阶不是曲线
#  (2) 实验三思考题第 6 题的贯穿答案：换成 timing（顺序、阻塞访存）核之后，
#      实验三任务 1 那张替换策略排行榜还成不成立？
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

$S --name lab4_lagfine --bench branchy --bench-args "2 4096 50" \
   --base "--cpu o3 --bp local" --vary width=1,2,3,4,6,8 --jobs 6 2>&1 | tail -3
$R results/lab4_lagfine.csv cycles ipc bp_committed bp_mispredicts bp_miss_rate squashed_insts
echo FINEDONE

# 实验三贯穿题：timing 核（顺序、访存阻塞）上重跑替换策略
$S --name lab4_l3timing --bench qnn --bench-args 8 \
   --base "--cpu timing --l1d-size 64kB --l1d-assoc 4" \
   --vary l1d-repl=lru,mru,random,lfu,bip --jobs 5 2>&1 | tail -3
$R results/lab4_l3timing.csv cycles ipc l1d_misses l1d_mshr_misses l1d_mlp
echo TIMINGDONE
