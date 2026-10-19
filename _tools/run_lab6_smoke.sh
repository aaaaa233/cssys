#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
OPT='8 0x01352505'
for m in l2bus membus; do
  echo "===== accel=$m (timing) ====="
  timeout 1200 $G --outdir=out/lab6/t_$m framework/cssys_se.py \
      --cmd bench/bin/riscv/qnn_accel --options "$OPT" \
      --cpu timing --accel $m 2>&1 \
    | grep -E 'checksum|done @|panic|fatal|Assertion|abort'
  grep -E '^system.accel' out/lab6/t_$m/stats.txt | sed 's/  */ /g' | head -14
done
echo SMOKEDONE
