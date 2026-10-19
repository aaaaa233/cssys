#!/bin/bash
# 修复后的两件事，缺一不可：
#  A) 原来卡死的 8 个种子现在都能跑完，而且 checksum 和 timing 核算出来的一致；
#  B) ★ 原来能跑完的配置，**周期数一个不差** —— 否则实验五/六已经定稿的
#     参考数据全部作废。修复是"只在死锁路径上加东西"，所以理论上必须逐位相同。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/verify
mkdir -p $OUT/logs

echo "===== A) 原来卡死的 8 个种子 ====="
for sd in 0x00003333 0x00003511 0x00005511 0x00005555 0x00005911 \
          0x00008511 0x0000d511 0x0000fd11; do
  t0=$SECONDS
  timeout 120 $G --outdir=$OUT/A_$sd $C --cmd bench/bin/riscv/qnn_accel_b2 \
      --options "8 $sd" --cpu o3 --accel l2bus --accel-pe 32 \
      > $OUT/logs/A_$sd.log 2>&1
  rc=$?; dt=$((SECONDS - t0))
  # 拿 timing 核跑一遍当"正确答案"（timing 核从来没卡过）
  timeout 120 $G --outdir=$OUT/T_$sd $C --cmd bench/bin/riscv/qnn_accel_b2 \
      --options "8 $sd" --cpu timing --accel l2bus --accel-pe 32 \
      > $OUT/logs/T_$sd.log 2>&1
  co3=$(grep -o 'checksum=0x[0-9a-f]*' $OUT/logs/A_$sd.log)
  cti=$(grep -o 'checksum=0x[0-9a-f]*' $OUT/logs/T_$sd.log)
  if [ $rc = 124 ]; then echo "  仍然卡死 $sd"
  elif [ "$co3" = "$cti" ] && [ -n "$co3" ]; then echo "  ok ${dt}s $sd  $co3  (与 timing 一致)"
  else echo "  ★校验和不符 $sd  o3=$co3 timing=$cti"; fi
done

echo
echo "===== B) 回归：修复前记录下来的周期数必须一模一样 ====="
# 左边是修复前实测值（out/lab7/opt、out/lab7/combo、out/lab7/final 里的数）
check () { local tag=$1 want=$2 bin=$3; shift 3
  $G --outdir=$OUT/B_$tag $C --cmd bench/bin/riscv/$bin \
     --options "8 0x01352505" --cpu o3 "$@" > $OUT/logs/B_$tag.log 2>&1
  local got=$(python3 framework/area.py $OUT/B_$tag --csv | tail -1 | cut -d, -f2)
  if [ "$got" = "$want" ]; then echo "  一致 $tag  $got"
  else echo "  ★变了 $tag  修复前=$want 修复后=$got"; fi
}
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"
CUT="--btb-entries 512 --lq 16 --sq 16"

check a5_all     92618 qnn_accel    --accel l2bus --accel-pe 32 $FREE
check B2_b2      80397 qnn_accel_b2 --accel l2bus --accel-pe 32 $FREE
check P48        74064 qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE
check Z_w4pe48   76102 qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE --width 4
check G_pe48_w6  74680 qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE $CUT --width 6
check G_pe48_w2  80802 qnn_accel_b2 --accel l2bus --accel-pe 48 $FREE $CUT --width 2
check W2_w2      87202 qnn_accel_b2 --accel l2bus --accel-pe 32 $FREE --width 2
check D_lat3    203773 qnn_dotp8x4c $FREE --dotp8-lat 3
check c5_all   1020074 qnn          $FREE

echo VERIFYDONE
