#!/bin/bash
cd /mnt/smartssd/wlx/cssys/bench || exit 1
for v in qnn qnn_dotp8 qnn_dotp8x2 qnn_dotp8x4; do
  echo "==== $v"
  riscv64-linux-gnu-objdump -d bin/riscv/$v | awk '/<dot_i8>:/{f=1} f{print} f&&/\tret/{exit}'
  echo
done
