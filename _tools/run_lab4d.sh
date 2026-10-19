#!/bin/bash
# 实验四补测 D：把随机数据对照组也扫成 1,2,3,4,6,8，
# 让指导书里给学生的那条命令和参考解答里的数据完全一致。
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

$S --name lab4_lag0 --bench branchy --bench-args "0 4096 50" \
   --base "--cpu o3 --bp local" --vary width=1,2,3,4,6,8 --jobs 6 2>&1 | tail -3
$R results/lab4_lag0.csv cycles ipc bp_committed bp_mispredicts bp_miss_rate squashed_insts
echo LAG0DONE

# 判决组也用同一组宽度重跑一次，写回 lab4_lag.csv（覆盖旧的 4 点版本）
$S --name lab4_lag --bench branchy --bench-args "2 4096 50" \
   --base "--cpu o3 --bp local" --vary width=1,2,3,4,6,8 --jobs 6 2>&1 | tail -3
$R results/lab4_lag.csv cycles ipc bp_committed bp_mispredicts bp_miss_rate squashed_insts
echo LAGDONE

# 任务 1 的宽度扫描：补一下主机耗时，用来校核指导书附录里"跑多久"的说法
python3 - <<'PY'
import csv
for n in ("lab4_width", "lab4_lag", "lab4_lag0"):
    rows = list(csv.DictReader(open("results/%s.csv" % n)))
    print(n, [(r.get("width"), r.get("host_seconds"), r.get("wall_seconds")) for r in rows])
PY
echo HOSTDONE
