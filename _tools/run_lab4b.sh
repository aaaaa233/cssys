#!/bin/bash
# 实验四补测：
#  (1) branchy mode2 上 local 的 42.85% 到底怎么来的？
#      课本上 2 bit 计数器对 TTTNNNN 应该只错 4/7=57%（折算到全部分支 28.6%），
#      实测却是 42.85%（折算到那条 if 分支 = 6/7 = 85.7%）。
#      假设：计数器是在 commit 时才更新的，深流水线里预测跑在更新前面。
#      判决：把机器变窄/变浅，在飞的实例变少，误预测率应当向课本值靠拢。
#  (2) 顺带测一下 IQ 尺寸，确认任务 6 里"瓶颈搬到 IQ"的说法
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

$S --name lab4_lag --bench branchy --bench-args "2 4096 50" \
   --base "--cpu o3 --bp local" --vary width=1,2,4,8 --jobs 4 2>&1 | tail -3
$R results/lab4_lag.csv insts cycles ipc bp_committed bp_mispredicts bp_miss_rate squashed_insts
echo LAGDONE

# 同一件事在 mode 0（随机）上做一遍作为对照：随机数据没有"模式"可学，
# 所以窄机器不应该把误预测率救回来。
$S --name lab4_lag0 --bench branchy --bench-args "0 4096 50" \
   --base "--cpu o3 --bp local" --vary width=1,2,4,8 --jobs 4 2>&1 | tail -3
$R results/lab4_lag0.csv cycles ipc bp_mispredicts bp_miss_rate
echo LAG0DONE

# IQ 尺寸扫描（任务 6 的依据）
$S --name lab4_iq --bench qnn --bench-args 8 \
   --base "--cpu o3 --lq 64" --vary iq=16,32,64,128 --jobs 4 2>&1 | tail -3
$R results/lab4_iq.csv cycles ipc iq_full_events lq_full_events rob_full_events l1d_mlp
echo IQDONE
