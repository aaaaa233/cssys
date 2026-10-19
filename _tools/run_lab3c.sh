#!/bin/bash
# 判决实验（第二次，这次假设是对的）：
#   L1 里 LIP 失效，是因为一个 64B 块被插进来之后，同一条 dot_i8 循环
#   紧接着又对它做了 63 次字节访问，第一次 touch() 就把它顶到 MRU，
#   "插在 LRU 位置"这个赌注在 1 个周期之内就被自己撤销了。
#   L1 平均每次插入被 touch 126 次（实测），赌注根本活不到下一次替换。
#
# 正对照：把同一个策略放到 L2。L1 已经把块内复用全部吸收掉，
#   L2 看到的是"每个块只被引用 1 次"的纯循环扫描——正是 LIP 论文里的场景。
#   L2 设成 64kB/4路 = 1024 行 < w1 的 1568 行，制造和 L1 一样的病态。
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

$S --name lab3_l2repl --bench qnn --bench-args 8 \
   --base "--cpu o3 --l2-size 64kB --l2-assoc 4" \
   --vary l2-repl=lru,lip,bip,mru,random,rrip,brrip --jobs 7 2>&1 | tail -3
$R results/lab3_l2repl.csv cycles ipc l2_accesses l2_misses l2_mshr_misses l2_miss_rate l1d_mshr_mpki
echo L2REPLDONE

# 同一组策略放在 L1（对照），确认差别来自"放在哪一级"而不是别的
$S --name lab3_l1repl_ctl --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 64kB --l1d-assoc 4" \
   --vary l1d-repl=lru,lip,bip,mru,random,rrip,brrip --jobs 7 2>&1 | tail -3
$R results/lab3_l1repl_ctl.csv cycles ipc l1d_accesses l1d_misses l1d_mshr_misses l1d_miss_rate
echo L1REPLDONE
