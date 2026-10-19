#!/bin/bash
# 实验三关键验证 + 实验四补跑
cd /mnt/smartssd/wlx/cssys || exit 1
S="python3 framework/sweep.py"
R="python3 framework/report.py"

# ------------------------------------------------------------------
# 假设：LIP/BIP/RRIP 这类"插入位置"策略之所以在 qnn 上完全失效，
#       是因为一个 64B 块被插入后马上又被同一段代码的后续 load 命中，
#       touch() 立刻把它提升到 MRU，插入位置被自己抵消。
# 判决实验：换成顺序核 timing（MLP=1，块内访问串行地一条条命中），
#       与乱序核 o3（MLP=15.6，块内访问大多在 MSHR 里合并掉了）对比。
# ------------------------------------------------------------------
$S --name lab3_promote --bench qnn --bench-args 8 \
   --base "--l1d-size 64kB --l1d-assoc 4" \
   --vary cpu=timing,o3 --vary l1d-repl=lru,lip,bip,mru,random --jobs 10 2>&1 | tail -3
$R results/lab3_promote.csv cycles ipc l1d_mshr_mpki l1d_misses l1d_mshr_misses l1d_mlp
echo PROMOTEDONE

# 低"块内复用"负载：pchase 每 64B 块只用 8 字节
$S --name lab3_promote_pc --bench pchase --bench-args "128 200000" \
   --base "--cpu o3 --l1d-size 64kB --l1d-assoc 4" \
   --vary l1d-repl=lru,lip,bip,mru,random,rrip,brrip --jobs 7 2>&1 | tail -3
$R results/lab3_promote_pc.csv cycles ipc l1d_mshr_mpki l1d_mlp
echo PCDONE

# ------------------------------------------------------------------
# 实验四补跑：修好 wbWidth 之后重扫宽度
# ------------------------------------------------------------------
$S --name lab4_width --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary width=1,2,4,8 --jobs 4 2>&1 | tail -3
$R results/lab4_width.csv cycles ipc rob_full_events iq_full_events \
   lq_full_events rename_block_frac squash_ratio
echo WIDTHDONE

# 实验四：宽度 x 预测器，补上 width=1
$S --name lab4_wxbp --bench branchy --bench-args "0 4096 50" \
   --base "--cpu o3" --vary width=1,2,4,8 --vary bp=local,tage --jobs 8 2>&1 | tail -3
$R results/lab4_wxbp.csv cycles ipc bp_miss_rate squash_ratio squashed_insts
echo WXBPDONE

# ------------------------------------------------------------------
# 实验三任务 4/5：预取器的收益与代价（含准确率/覆盖率）
# ------------------------------------------------------------------
$S --name lab3_pf --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary l1d-pf=none,tagged,stride,bop,ampm,isb --jobs 6 2>&1 | tail -3
$R results/lab3_pf.csv cycles ipc l1d_mshr_mpki l1d_mlp \
   l1d_pf_issued l1d_pf_useful l1d_pf_unused l1d_pf_accuracy l1d_pf_coverage
echo PFDONE

# 预取 vs 加大容量：同一张表里比
$S --name lab3_pf_vs_size --bench qnn --bench-args 8 \
   --base "--cpu o3" --vary l1d-size=32kB,64kB,128kB \
   --vary l1d-pf=none,stride --jobs 6 2>&1 | tail -3
$R results/lab3_pf_vs_size.csv cycles ipc l1d_mshr_mpki l1d_pf_accuracy dram_bytes
echo PFSIZEDONE

# 预取器在没有空间局部性的负载上（代价暴露）
$S --name lab3_pf_pchase --bench pchase --bench-args "256 200000" \
   --base "--cpu o3" --vary l1d-pf=none,tagged,stride,ampm --jobs 4 2>&1 | tail -3
$R results/lab3_pf_pchase.csv cycles ipc l1d_mshr_mpki \
   l1d_pf_issued l1d_pf_useful l1d_pf_accuracy dram_bytes
echo PFPCDONE
