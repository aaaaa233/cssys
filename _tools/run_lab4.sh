#!/bin/bash
# 实验四参考数据：乱序执行与分支预测
# 说明：branchy 用 n=4096（数组 16KB，稳稳装进 32kB 的 L1D），
#       这样测出来的差异只来自分支预测，不掺 Cache 效应。
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

# ---- 任务 1：发射宽度 ----
$S --name lab4_width --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary width=1,2,4,8 --jobs 4 2>&1 | tail -3
$R results/lab4_width.csv cycles ipc rob_full_events iq_full_events \
   lq_full_events rename_block_frac squash_ratio
echo WIDTHDONE

# ---- 任务 2：瓶颈定位。先 ROB（预期毫无变化），再 LQ（预期真有收益）----
$S --name lab4_rob --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary rob=32,64,128,192,384 --jobs 5 2>&1 | tail -3
$R results/lab4_rob.csv cycles ipc rob_full_events lq_full_events iq_full_events
echo ROBDONE

$S --name lab4_lq --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary lq=8,16,32,64,128 --jobs 5 2>&1 | tail -3
$R results/lab4_lq.csv cycles ipc lq_full_events rob_full_events \
   iq_full_events l1d_mlp load_to_use
echo LQDONE

# ---- 任务 3(a)：在 qnn 上换分支预测器（预期：毫无意义）----
$S --name lab4_bp_qnn --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary bp=local,bimode,tournament,tage,ltage --jobs 5 2>&1 | tail -3
$R results/lab4_bp_qnn.csv cycles ipc bp_committed bp_mispredicts \
   bp_miss_rate squash_ratio
echo BPQNNDONE

# ---- 任务 3(b)：换负载。同一份代码，三种数据 ----
$S --name lab4_branchy --bench branchy --bench-args "0 4096 50" \
   --base "--cpu o3" --vary bp=local,bimode,tournament,tage --jobs 4 2>&1 | tail -3
$S --name lab4_branchy1 --bench branchy --bench-args "1 4096 50" \
   --base "--cpu o3" --vary bp=local,bimode,tournament,tage --jobs 4 2>&1 | tail -3
$S --name lab4_branchy2 --bench branchy --bench-args "2 4096 50" \
   --base "--cpu o3" --vary bp=local,bimode,tournament,tage --jobs 4 2>&1 | tail -3
for m in 0 1 2; do
  echo "--- branchy mode $m ---"
  if [ "$m" = "0" ]; then C=results/lab4_branchy.csv; else C=results/lab4_branchy$m.csv; fi
  $R $C insts cycles ipc bp_committed bp_mispredicts bp_miss_rate squash_ratio
done
echo BRANCHYDONE

# ---- 任务 4：宽度 x 预测器（加宽会不会放大误预测代价）----
$S --name lab4_wxbp --bench branchy --bench-args "0 4096 50" \
   --base "--cpu o3" --vary width=2,4,8 --vary bp=local,tage --jobs 6 2>&1 | tail -3
$R results/lab4_wxbp.csv cycles ipc bp_miss_rate squash_ratio squashed_insts
echo WXBPDONE

# ---- 任务 5：BTB 容量（目标预测 vs 方向预测）----
$S --name lab4_btb --bench qnn --bench-args 8 \
   --base "--cpu o3 --bp tournament" \
   --vary btb-entries=8,32,128,512,4096 --jobs 5 2>&1 | tail -3
$R results/lab4_btb.csv cycles ipc bp_mispredicts bp_miss_predictor \
   bp_miss_btb btb_hit_rate
echo BTBDONE

# ---- 任务 6：把核内资源全部加倍，看总收益（通往实验 5 的桥）----
$S --name lab4_allin --bench qnn --bench-args 8 \
   --base "--cpu o3 --width 8 --rob 384 --iq 128 --lq 128 --sq 64 --int-regs 512 --bp tage_sc_l" \
   --vary l1d-size=32kB --jobs 1 2>&1 | tail -3
$R results/lab4_allin.csv cycles ipc rob_full_events iq_full_events \
   lq_full_events bp_miss_rate squash_ratio
echo ALLINDONE
