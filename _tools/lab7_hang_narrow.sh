#!/bin/bash
# 缩小范围：坏种子 0x00003333，卡在第二层(rows=10 n=128 batch=2)的加速器作业上。
# CPU 已经把 GO 提交了，所以问题在加速器侧。逐个变量试。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
C=framework/cssys_se.py
OUT=out/lab7/narrow
mkdir -p $OUT/logs

probe () { local tag=$1; shift; local bin=$1; shift; local sd=$1; shift
  local t0=$SECONDS
  timeout 90 $G --outdir=$OUT/$tag $C --cmd bench/bin/riscv/$bin \
      --options "8 $sd" "$@" > $OUT/logs/$tag.log 2>&1
  local rc=$?; local dt=$((SECONDS - t0))
  if [ $rc = 124 ]; then echo "TIMEOUT  $tag"
  elif [ $rc != 0 ]; then echo "ERROR($rc) $tag : $(tail -2 $OUT/logs/$tag.log | head -1)"
  else echo "ok ${dt}s  $tag  $(grep -m1 'checksum' $OUT/logs/$tag.log)"; fi
}

S=0x00003333

echo "===== CPU 模型 ====="
probe N_o3      qnn_accel_b2 $S --cpu o3     --accel l2bus --accel-pe 32
probe N_timing  qnn_accel_b2 $S --cpu timing --accel l2bus --accel-pe 32
probe N_atomic  qnn_accel_b2 $S --cpu atomic --accel l2bus --accel-pe 32

echo
echo "===== 挂载点 ====="
probe N_membus  qnn_accel_b2 $S --cpu o3 --accel membus --accel-pe 32

echo
echo "===== outstanding（每次能挂几个访存请求）====="
for o in 1 2 4 8 16; do
  probe N_out$o qnn_accel_b2 $S --cpu o3 --accel l2bus --accel-pe 32 --accel-outstanding $o
done

echo
echo "===== 算力 pe ====="
for p in 8 16 32 64; do
  probe N_pe$p qnn_accel_b2 $S --cpu o3 --accel l2bus --accel-pe $p
done

echo
echo "===== batch（第二层的 n/rows 会跟着变）====="
probe N_b1 qnn_accel    $S --cpu o3 --accel l2bus --accel-pe 32
probe N_b4 qnn_accel_b4 $S --cpu o3 --accel l2bus --accel-pe 32
probe N_b8 qnn_accel_b8 $S --cpu o3 --accel l2bus --accel-pe 32

echo
echo "===== Cache 行大小（segs 切块和它有关）====="
probe N_line32  qnn_accel_b2 $S --cpu o3 --accel l2bus --accel-pe 32 --cacheline 32
probe N_line128 qnn_accel_b2 $S --cpu o3 --accel l2bus --accel-pe 32 --cacheline 128

echo NARROWDONE
