#!/bin/bash
# Re-derive the task-5 checksum table at the DOCUMENTED seed 0x01352505.
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
for v in qnn qnn_dotp8my qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c; do
  out=$($G --outdir=/tmp/ck_$v framework/cssys_se.py \
        --cmd bench/bin/riscv/$v --options "8 0x01352505" \
        --cpu atomic 2>/dev/null | grep -i checksum)
  printf '%-14s %s\n' "$v" "$out"
done
echo "---- md5 ----"
md5sum bench/bin/riscv/qnn bench/bin/riscv/qnn_dotp8my | awk '{print $1, $2}'
echo CHKDONE
