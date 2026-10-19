#!/bin/bash
# 实验七 参考数据 C6：修死锁之后重做两件事
#
# 1) 全种子回扫 —— 确认死锁真的没了（修复前 qnn_accel_b2 有 8/69 卡死）
# 2) ★★ 排名稳定性 —— 学生用自己学号的种子。如果 width 的排名会随种子变，
#    任务 4 就没有标准答案，这道题不能出。**这是实验七能否成立的前提。**
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/robust
mkdir -p $OUT/logs
rm -f $OUT/hang.txt

FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"

# ---------- 1) 全种子回扫 ----------
scan1 () {
  local bin=$1 sd=$2
  timeout 90 gem5/build/RISCV/gem5.opt --outdir=$OUT/s_${bin}_${sd} \
      framework/cssys_se.py --cmd bench/bin/riscv/$bin --options "8 $sd" \
      --cpu o3 --accel l2bus --accel-pe 32 > /dev/null 2>&1
  [ $? = 124 ] && echo "HANG $bin $sd" >> $OUT/hang.txt
  rm -rf $OUT/s_${bin}_${sd}
}
export -f scan1; export OUT

for i in $(seq 0 79); do printf '0x0000%04x\n' $((i * 819 + 273)); done > $OUT/seeds.txt
printf '0x00003333\n0x00003511\n0x00005511\n0x00005555\n0x00005911\n0x00008511\n0x0000d511\n0x0000fd11\n' >> $OUT/seeds.txt
for bin in qnn_accel qnn_accel_b2 qnn_accel_b4 qnn_accel_b8; do
  while read -r sd; do echo "$bin $sd"; done < $OUT/seeds.txt
done | xargs -P 12 -n 2 bash -c 'scan1 "$0" "$1"'

echo "===== 1) 死锁回扫：共 $(wc -l < $OUT/seeds.txt) 个种子 × 4 个二进制 ====="
if [ -s $OUT/hang.txt ]; then echo "  ★还有卡死的："; cat $OUT/hang.txt
else echo "  全部跑完，没有卡死"; fi

# ---------- 2) 排名稳定性 ----------
run () { local tag=$1; shift; local bin=$1; shift; local sd=$1; shift
  $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
     --options "8 $sd" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1 || echo "   FAIL $tag"
}

echo
echo "===== 2) 四个种子 × 七个配置 ====="
for sd in 0x01352505 0x00001234 0x0000abcd 0x00003333; do
  t=${sd: -4}
  run R_${t}_base qnn "$sd"
  for w in 2 3 4 5 6; do
    run R_${t}_w$w qnn_accel_b2 "$sd" --accel l2bus --accel-pe 48 $FREE $CUT --width $w
  done
  run R_${t}_w8 qnn_accel_b2 "$sd" --accel l2bus --accel-pe 48 $FREE $CUT
done

echo
python3 framework/area.py $OUT/R_* --csv
echo ROBUSTDONE
