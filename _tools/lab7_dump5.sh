#!/bin/bash
# dump4 的 (e) 被一个不存在的选项 --l2-mshrs 带崩了，重来。
# 这张表是任务 4d 的标准答案：35.4 A 的裕量，逐个候选试一遍，看有没有一个划算的。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump4
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"
S=0x01352505
B="--accel l2bus --accel-pe 48 $FREE $CUT --width 6"
r () { local tag=$1; shift; local bin=$1; shift
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "8 $S" --cpu o3 \
     "$@" > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
echo "########## (e) 35.4 A 裕量的全部候选（底盘 b4/pe48/w6/564.6A/74256） ##########"
r E_l2a16   qnn_accel_b4 $B --l2-assoc 16
r E_l1dm16  qnn_accel_b4 $B --l1d-mshrs 16
r E_l2mshr  qnn_accel_b4 $B --l2-mshr 32
r E_pf      qnn_accel_b4 $B --l2-prefetcher stride
r E_out16   qnn_accel_b4 $B --accel-outstanding 16
r E_l2160   qnn_accel_b4 $B --l2-size 160kB
python3 framework/area.py $OUT/E_base $OUT/E_lqsq32 $OUT/E_l1d16 $OUT/E_l1i4 \
    $OUT/E_pe64 $OUT/E_rob192 $OUT/E_iq96 $OUT/E_regs256 $OUT/E_l2a16 $OUT/E_w8 \
    $OUT/E_l1dm16 $OUT/E_l2mshr $OUT/E_pf $OUT/E_out16 $OUT/E_l2160 --csv 2>&1

echo
echo "########## (k) 帕累托前沿最终版：b4 底盘 × width 2..8 ##########"
for w in 2 3 4 5 6 8; do
  r K_w$w qnn_accel_b4 --accel l2bus --accel-pe 48 $FREE $CUT --width $w
done
python3 framework/area.py $OUT/K_w2 $OUT/K_w3 $OUT/K_w4 $OUT/K_w5 $OUT/K_w6 $OUT/K_w8 --csv

echo
echo "########## (l) 取指假说的第三次交叉验证：qnn 的基本块长度 ##########"
for w in 2 4 6 8; do
  printf 'qnn  w=%-2s ' $w
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' out/lab7/dump3/C_w$w/stats.txt \
    | grep -E 'system.cpu.numCycles |system.cpu.fetch.predictedBranches|system.cpu.fetch.cycles |system.cpu.decode.blockedCycles|system.cpu.commit.instsCommitted' \
    | awk '{printf "%s=%s  ", $1, $2}'; echo
done
echo "--- ROI 指令数（从 run.log 的 area.py 口径）---"
python3 framework/area.py out/lab7/dump3/C_w2 out/lab7/dump3/C_w4 \
        out/lab7/dump3/C_w6 out/lab7/dump3/C_w8 --csv

echo
echo "########## (m) checksum ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP5DONE
