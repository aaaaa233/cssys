#!/bin/bash
cd /mnt/smartssd/wlx/cssys/bench || exit 1
OD=riscv64-linux-gnu-objdump
for v in qnn qnn_dotp8; do
  echo "########## $v ##########"
  $OD -d --no-show-raw-insn bin/riscv/$v \
    | awk '/<dot_i8>:/{f=1} f{print} f&&/ret/{exit}'
done
echo "########## checksums ##########"
cd /mnt/smartssd/wlx/cssys || exit 1
for v in qnn qnn_dotp8 qnn_dotp8my qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c; do
  printf "%-14s " "$v"
  gem5/build/RISCV/gem5.opt --outdir=/tmp/ck_$v framework/cssys_se.py \
    --cmd bench/bin/riscv/$v --options "8 0x01352505" --cpu atomic 2>/dev/null \
    | grep -E "checksum|histogram" | tr '\n' '|'
  echo
done
echo DISDONE
