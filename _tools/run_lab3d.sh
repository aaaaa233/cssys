#!/bin/bash
# 验证自己写进 gem5 的替换策略 CssysRP
#   判据一：cssys(LRU 口径) 必须和 gem5 自带 lru 逐位相同
#   判据二：cssys_mru      必须和 gem5 自带 mru 逐位相同
# 顺便把新加的统计量（refsPerInsertion / avgFirstTouchDelay）在 L1 和 L2 上各测一遍
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

$S --name lab3_mine --bench qnn --bench-args 8 \
   --base "--cpu o3 --l1d-size 64kB --l1d-assoc 4" \
   --vary l1d-repl=lru,cssys,mru,cssys_mru --jobs 4 2>&1 | tail -3
$R results/lab3_mine.csv cycles ipc l1d_misses l1d_mshr_misses
echo MINEDONE

echo '--- 新统计量长什么样（L1，cssys 即 LRU 口径）'
grep -E 'replacement_policy|cssys' out/sweeps/lab3_mine/p001_l1d-repl-cssys/stats.txt | head -30
echo STAT1DONE

# 同一份代码放到 L2：看 refsPerInsertion 从 112 掉到 1
$S --name lab3_mine_l2 --bench qnn --bench-args 8 \
   --base "--cpu o3 --l2-size 64kB --l2-assoc 4" \
   --vary l2-repl=cssys --jobs 1 2>&1 | tail -3
echo '--- L2 上的同一组统计量'
grep -E 'replacement_policy' out/sweeps/lab3_mine_l2/p000_l2-repl-cssys/stats.txt | head -30
echo STAT2DONE
