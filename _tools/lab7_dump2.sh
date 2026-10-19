#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump
mkdir -p $OUT/logs
S="8 0x01352505"

echo "########## 4) 任务3 单旋钮扫描（27 点） ##########"
for k in l1i l1d l2 width rob iq regs; do
  echo "--- $k ---"
  python3 framework/area.py out/sweeps/lab7_s_$k/p*/ --csv | tail -n +2
done

echo
echo "########## 9) L2 256->128 在两个程序上的差别（任务5 第5问） ##########"
q () { local tag=$1; shift; local bin=$1; shift
  [ -d $OUT/$tag ] || $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
     --options "$S" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
q L_sw256   qnn
q L_sw128   qnn          --l2-size 128kB
q L_ac256   qnn_accel    --accel l2bus --accel-pe 32
q L_ac128   qnn_accel    --accel l2bus --accel-pe 32 --l2-size 128kB
python3 framework/area.py $OUT/L_sw256 $OUT/L_sw128 $OUT/L_ac256 $OUT/L_ac128 --csv

echo
echo "########## 10) 任务3 第5问 width 陷阱：纯软件 qnn 上的 w2/4/6/8 ##########"
python3 framework/area.py out/sweeps/lab7_s_width/p*/ --csv | tail -n +2

echo
echo "########## 11) 三个免费旋钮 btb/lq/sq 在两个程序上（任务4 提示的答案） ##########"
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
q N_ac_none  qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE
q N_ac_btb   qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE --btb-entries 512
q N_ac_lqsq  qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE --lq 16 --sq 16
q N_ac_all   qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE --btb-entries 512 --lq 16 --sq 16
q N_sw_none  qnn $FREE
q N_sw_all   qnn $FREE --btb-entries 512 --lq 16 --sq 16
python3 framework/area.py $OUT/N_ac_none $OUT/N_ac_btb $OUT/N_ac_lqsq $OUT/N_ac_all \
                          $OUT/N_sw_none $OUT/N_sw_all --csv

echo
echo "########## 12) 实验五那条路在预算下能到哪（任务4 的对照） ##########"
q V_d1 qnn_dotp8x4c $FREE --dotp8-lat 1
q V_d2 qnn_dotp8x4c $FREE --dotp8-lat 2
q V_d3 qnn_dotp8x4c $FREE --dotp8-lat 3
q V_d3c qnn_dotp8x4c $FREE --dotp8-lat 3 --btb-entries 512 --lq 16 --sq 16 --width 6
python3 framework/area.py $OUT/V_d1 $OUT/V_d2 $OUT/V_d3 $OUT/V_d3c --csv

echo
echo "########## 13) 预算内买不到的：pe64 与 accel-outstanding ##########"
CUT="--btb-entries 512 --lq 16 --sq 16"
q O_pe48_o8  qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE $CUT --width 6
q O_pe48_o16 qnn_accel_b2 --accel l2bus --accel-pe 48 --accel-outstanding 16 $FREE $CUT --width 6
q O_pe64_w6  qnn_accel_b2 --accel l2bus --accel-pe 64 $FREE $CUT --width 6
q O_b4_w6    qnn_accel_b4 --accel l2bus --accel-pe 48 $FREE $CUT --width 6
q O_b8_w6    qnn_accel_b8 --accel l2bus --accel-pe 48 $FREE $CUT --width 6
q O_b2_mem   qnn_accel_b2 --accel membus --accel-pe 48 $FREE $CUT --width 6
python3 framework/area.py $OUT/O_pe48_o8 $OUT/O_pe48_o16 $OUT/O_pe64_w6 \
                          $OUT/O_b4_w6 $OUT/O_b8_w6 $OUT/O_b2_mem --csv

echo
echo "########## 14) checksum 自检 ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP2DONE
