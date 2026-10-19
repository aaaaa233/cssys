#!/bin/bash
# 实验四补测 E：把"全都加"那一档拆开，否则参考解答里的交付物表格没法诚实填写。
#  (1) ROB 第二轮：在 LQ/IQ 已经放开之后，ROB 192->384 到底值多少？
#      （任务 2a 里它值 0，任务 2c 之后 rob_full_events 从 0 变成 68147，
#        所以必须单独量一次，不能拿 allin 的总收益去顶。）
#  (2) 物理整数寄存器：allin 里改了 --int-regs 512，单独量它。
#  (3) 分支预测器在 allin 那一档里贡献了多少（qnn 上预期为 0）。
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

# (1) LQ/IQ 放开之后再加 ROB
$S --name lab4_rob2 --bench qnn --bench-args 8 \
   --base "--cpu o3 --lq 64 --iq 128" --vary rob=192,256,384,512 --jobs 4 2>&1 | tail -3
$R results/lab4_rob2.csv cycles ipc rob_full_events iq_full_events lq_full_events \
   sq_full_events l1d_mlp load_to_use
echo ROB2DONE

# (2) 物理寄存器
$S --name lab4_regs --bench qnn --bench-args 8 \
   --base "--cpu o3 --lq 64 --iq 128 --rob 384" --vary int-regs=192,256,384,512 --jobs 4 2>&1 | tail -3
$R results/lab4_regs.csv cycles ipc rob_full_events iq_full_events sq_full_events l1d_mlp
echo REGSDONE

# (3) 在满配核上换预测器
$S --name lab4_allbp --bench qnn --bench-args 8 \
   --base "--cpu o3 --width 8 --rob 384 --iq 128 --lq 128 --sq 64 --int-regs 512" \
   --vary bp=local,tournament,tage_sc_l --jobs 3 2>&1 | tail -3
$R results/lab4_allbp.csv cycles ipc bp_mispredicts bp_miss_rate squashed_insts \
   iq_full_events rob_full_events
echo ALLBPDONE
