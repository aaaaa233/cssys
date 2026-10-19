#!/bin/bash
# 任务 1 反面教材：去掉 fence 之后会怎样？
# 顺序核(timing)看不出问题，乱序核(o3)直接崩——这正是要学生亲眼看到的对比。
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
OPT='8 0x01352505'
for c in timing o3; do
  for b in qnn_accel qnn_accel_nofence; do
    echo "===== cpu=$c bench=$b ====="
    timeout 900 $G --outdir=out/lab6/nf_${c}_${b} framework/cssys_se.py \
        --cmd bench/bin/riscv/$b --options "$OPT" \
        --cpu $c --accel l2bus --accel-pe 32 2>&1 \
      | grep -E 'checksum|panic|fatal|Assertion|Program aborted' | head -4
  done
done
echo NOFENCEDONE
