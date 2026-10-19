#!/bin/bash
# 收尾：把 batch 的四条曲线补齐，专门为了回答"b8 为什么反而慢"。
# dump7 已经证明 b2/b4 的屋顶完全重合（bytesPerCycle 都钉死在 21.20），
# 差别只在算术强度。如果 b8 的算术强度真的是 b4 的两倍，它的 macsPerCycle
# 上限应该到 163——但它跑得比 b4 慢。到底慢在 CPU 侧还是加速器侧？
# 判据：总周期 - jobCycles = "非加速器时间"。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/dump8
mkdir -p $OUT/logs
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"
S=0x01352505
r () { local tag=$1 bin=$2 pe=$3
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin --options "8 $S" --cpu o3 \
     --accel l2bus --accel-pe $pe $FREE $CUT --width 6 \
     > $OUT/logs/$tag.log 2>&1 || echo "  FAIL $tag"
}
echo "########## (v) b1/b2/b4/b8 × pe 48/83/128，w6 固定 ##########"
for pe in 48 83 128; do
  r V_b1_$pe qnn_accel    $pe
  r V_b8_$pe qnn_accel_b8 $pe
done
python3 framework/area.py $OUT/V_* --csv

echo
echo "--- 拆成 CPU 侧 / 加速器侧（非加速器时间 = 总周期 - jobCycles）---"
printf '%-10s %-8s %10s %10s %10s %10s %12s %12s %8s\n' \
   bin pe cycles jobCycles 非加速器 macs macsPerCyc bytesPerCyc dmiss
for t in V_b1_48 V_b1_83 V_b1_128 V_b8_48 V_b8_83 V_b8_128; do
  d=$OUT/$t
  awk -v tag=$t '/^-+ Begin Simulation Statistics/{n++} n==2' $d/stats.txt > /tmp/s.$$
  cyc=$(awk '/^system.cpu.numCycles /{print $2}' /tmp/s.$$)
  jc=$(awk  '/^system.accel.jobCycles/{print $2}' /tmp/s.$$)
  mc=$(awk  '/^system.accel.macs /{print $2}' /tmp/s.$$)
  mpc=$(awk '/^system.accel.macsPerCycle/{print $2}' /tmp/s.$$)
  bpc=$(awk '/^system.accel.bytesPerCycle/{print $2}' /tmp/s.$$)
  dm=$(awk  '/^system.cpu.dcache.overallMisses::total/{print $2}' /tmp/s.$$)
  printf '%-10s %-8s %10s %10s %10s %10s %12s %12s %8s\n' \
     "${t%_*}" "${t##*_}" "$cyc" "$jc" "$((cyc-jc))" "$mc" "$mpc" "$bpc" "$dm"
done
echo "--- 同底盘 b2/b4 对照（dump6/dump7 已有）---"
for d in out/lab7/dump6/N_b4_w6_48 out/lab7/dump7/R_best \
         out/lab7/dump7/S_b2_48 out/lab7/dump7/S_b2_128; do
  awk '/^-+ Begin Simulation Statistics/{n++} n==2' $d/stats.txt > /tmp/s.$$
  cyc=$(awk '/^system.cpu.numCycles /{print $2}' /tmp/s.$$)
  jc=$(awk  '/^system.accel.jobCycles/{print $2}' /tmp/s.$$)
  mpc=$(awk '/^system.accel.macsPerCycle/{print $2}' /tmp/s.$$)
  bpc=$(awk '/^system.accel.bytesPerCycle/{print $2}' /tmp/s.$$)
  dm=$(awk  '/^system.cpu.dcache.overallMisses::total/{print $2}' /tmp/s.$$)
  printf '%-32s %10s %10s %10s %12s %12s %8s\n' "$d" "$cyc" "$jc" "$((cyc-jc))" "$mpc" "$bpc" "$dm"
done
rm -f /tmp/s.$$

echo
echo "########## (w) checksum ##########"
grep -h checksum $OUT/logs/*.log | sort | uniq -c
echo DUMP8DONE
