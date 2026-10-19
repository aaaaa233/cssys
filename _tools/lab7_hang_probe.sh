#!/bin/bash
# 实验七 阻断性问题排查：qnn_accel_b2 + 种子 0x00001234 跑了 21 分钟没结束
#
# 已知：同一种子下 qnn（纯软件）正常结束；
#       qnn_accel_b2 + 种子 0x01352505 正常结束（30 秒）。
# 所以怀疑是**数据相关的死循环**，而不是配置问题。
# 学生用的是自己学号的种子，这个必须查清楚，否则实验七开不了。
#
# 每个点最多给 90 秒，超时就记 TIMEOUT。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/hang
mkdir -p $OUT/logs

probe () {   # probe <标签> <二进制> <种子> <额外参数...>
  local tag=$1; shift; local bin=$1; shift; local sd=$1; shift
  local t0=$SECONDS
  timeout 90 $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
      --options "8 $sd" --cpu o3 "$@" > $OUT/logs/$tag.log 2>&1
  local rc=$?
  local dt=$((SECONDS - t0))
  if [ $rc = 124 ]; then
    echo "TIMEOUT  $tag  (>90s)"
  elif [ $rc != 0 ]; then
    echo "ERROR($rc) $tag"
  else
    local cyc=$(grep -m1 'cssys. done' $OUT/logs/$tag.log)
    echo "ok ${dt}s  $tag  $cyc"
  fi
}

A="--accel l2bus --accel-pe 32"
FREE="--l2-size 128kB --l1i-size 2kB --l1d-size 8kB --rob 128 --int-regs 160"

echo "===== 1) 换二进制，固定坏种子 0x00001234、固定默认配置 ====="
probe H_sw_1234    qnn          0x00001234
probe H_b1_1234    qnn_accel    0x00001234 $A
probe H_b2_1234    qnn_accel_b2 0x00001234 $A
probe H_b4_1234    qnn_accel_b4 0x00001234 $A
probe H_b8_1234    qnn_accel_b8 0x00001234 $A
probe H_d8_1234    qnn_dotp8x4c 0x00001234

echo
echo "===== 2) 固定 qnn_accel_b2 + 默认加速器配置，扫种子 ====="
for sd in 0x01352505 0x00001234 0x0000abcd 0x00000001 0x00001111 0x00002222 \
          0x00003333 0x00004444 0x00005555 0x00006666 0x00007777 0x00008888 \
          0x00009999 0x0000aaaa 0x0000bbbb 0x0000cccc 0x0000dddd 0x0000eeee; do
  probe H_seed_$sd qnn_accel_b2 $sd $A
done

echo
echo "===== 3) 坏种子 + 不同挂载点/算力（看是不是加速器本身的问题）====="
probe H_mem_1234   qnn_accel_b2 0x00001234 --accel membus --accel-pe 32
probe H_pe8_1234   qnn_accel_b2 0x00001234 --accel l2bus --accel-pe 8
probe H_out1_1234  qnn_accel_b2 0x00001234 --accel l2bus --accel-pe 32 --accel-outstanding 1
probe H_free_1234  qnn_accel_b2 0x00001234 $A $FREE

echo HANGPROBEDONE
