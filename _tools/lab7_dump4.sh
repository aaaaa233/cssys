#!/bin/bash
# 最后一批。四件事：
#  (e) 把 35.4 A 裕量真的花一遍 —— 任务 4d 要求"给出考虑过又放弃的选项"，
#      参考解答自己没试过就没资格这么要求。
#  (f) ★ 实验六附录 C 留的那个未解之谜有救了：
#      lab6 猜 batch=8 时 CPU 侧缓冲区涨到约 11.4 KB。实验七把 L1D 砍到 8 kB，
#      b8 就变慢了 7.5%。如果把 L1D 单独放回 32 kB，b8 应该恢复 —— 这是个可证伪预测。
#  (g) LQ/SQ 单独一项到底值多少：dump3 已证明 BTB 4096->512 在两个程序上都逐位免费，
#      所以纯软件上那 +42% 应该**全部**来自 LQ/SQ。要单独测出来。
#  (h) 取指假说的交叉验证：基本块平均 7 条 -> ceil(7/w) 解释了 w6≈w4。
#      qnn_dotp8x4c 的基本块更长，它的 width 曲线形状应该不同。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump4
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"
S=0x01352505

r () { local tag=$1; shift; local bin=$1; shift
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "8 $S" --cpu o3 \
     "$@" > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
B="--accel l2bus --accel-pe 48 $FREE $CUT --width 6"

echo "########## (e) 把 35.4 A 裕量花掉的所有候选（底盘 = b4/pe48/w6/564.6A） ##########"
r E_base   qnn_accel_b4 $B
r E_lqsq32 qnn_accel_b4 --accel l2bus --accel-pe 48 $FREE --btb-entries 512 --width 6
r E_l1d16  qnn_accel_b4 $B --l1d-size 16kB
r E_l1i4   qnn_accel_b4 $B --l1i-size 4kB
r E_pe64   qnn_accel_b4 $B --accel-pe 64
r E_rob192 qnn_accel_b4 $B --rob 192
r E_iq96   qnn_accel_b4 $B --iq 96
r E_regs256 qnn_accel_b4 $B --int-regs 256
r E_mshr   qnn_accel_b4 $B --l2-mshrs 32
r E_l2a16  qnn_accel_b4 $B --l2-assoc 16
r E_w8     qnn_accel_b4 --accel l2bus --accel-pe 48 $FREE $CUT --width 8
python3 framework/area.py $OUT/E_* --csv

echo
echo "########## (f) 实验六附录 C：b8 变慢是不是因为 L1D 装不下了 ##########"
for b in b2 b4 b8; do
  r F_${b}_l1d8  qnn_accel_$b $B
  r F_${b}_l1d32 qnn_accel_$b --accel l2bus --accel-pe 48 --l2-size 128kB \
      --l1i-size 2kB --l1d-size 32kB --rob 128 --int-regs 160 $CUT --width 6
done
python3 framework/area.py $OUT/F_* --csv
echo "--- 各自的 L1D/L2 缺失 ---"
for t in F_b2_l1d8 F_b4_l1d8 F_b8_l1d8 F_b2_l1d32 F_b4_l1d32 F_b8_l1d32; do
  printf '%-14s ' $t
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/$t/stats.txt | grep -E \
    'system.cpu.dcache.overallMisses::total|system.l2.overallMisses::total' \
    | awk '{printf "%s=%s  ", $1, $2}'
  echo
done

echo
echo "########## (g) LQ/SQ 单独一项在两个程序上的价钱 ##########"
r G_sw_none  qnn $FREE
r G_sw_btb   qnn $FREE --btb-entries 512
r G_sw_lqsq  qnn $FREE --lq 16 --sq 16
r G_sw_lq    qnn $FREE --lq 16
r G_sw_sq    qnn $FREE --sq 16
r G_ac_none  qnn_accel_b4 --accel l2bus --accel-pe 48 $FREE --width 6
r G_ac_lqsq  qnn_accel_b4 --accel l2bus --accel-pe 48 $FREE --lq 16 --sq 16 --width 6
python3 framework/area.py $OUT/G_sw_none $OUT/G_sw_btb $OUT/G_sw_lqsq $OUT/G_sw_lq \
                          $OUT/G_sw_sq $OUT/G_ac_none $OUT/G_ac_lqsq --csv

echo
echo "########## (h) 取指假说：基本块长度 vs width 曲线 ##########"
for w in 2 4 6 8; do r H_d8_w$w qnn_dotp8x4c --dotp8-lat 3 --width $w; done
python3 framework/area.py $OUT/H_d8_w2 $OUT/H_d8_w4 $OUT/H_d8_w6 $OUT/H_d8_w8 --csv
echo "--- 基本块长度 = ROI 指令数 / fetch 预测为 taken 的分支数 ---"
for t in H_d8_w8 H_d8_w6 H_d8_w4; do
  printf '%-10s ' $t
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/$t/stats.txt | grep -E \
    'system.cpu.numCycles|system.cpu.commit.instsCommitted::total|system.cpu.fetch.predictedBranches|system.cpu.fetch.cycles|system.cpu.decode.blockedCycles' \
    | awk '{printf "%s=%s  ", $1, $2}'
  echo
done
echo "--- 对照：qnn 自己的 ---"
for w in 8 6 4 2; do
  printf 'qnn_w%-2s ' $w
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' out/lab7/dump3/C_w$w/stats.txt | grep -E \
    'system.cpu.commit.instsCommitted::total|system.cpu.fetch.predictedBranches' \
    | awk '{printf "%s=%s  ", $1, $2}'
  echo
done

echo
echo "########## (i) L2 免费的边界在哪：DRAM 行数 / L2 缺失 ##########"
for sz in 64kB 128kB 256kB 512kB; do
  r I_l2$sz qnn --l2-size $sz
  printf 'l2=%-6s ' $sz
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $OUT/I_l2$sz/stats.txt | grep -E \
    'system.cpu.numCycles|system.l2.overallMisses::total|system.mem_ctrl.dram.bytesRead::total' \
    | awk '{printf "%s=%s  ", $1, $2}'
  echo
done

echo
echo "########## (j) checksum 自检 ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP4DONE
