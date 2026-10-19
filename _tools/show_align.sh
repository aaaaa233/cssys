#!/bin/bash
cd /mnt/smartssd/wlx/cssys/bench || exit 1
make noalign
echo
printf "%-22s %-18s %s\n" 变体 dot_i8地址 mod64
for b in qnn qnn_noroi qnn_noalign qnn_noalign_noroi; do
  a=$(riscv64-linux-gnu-nm bin/riscv/$b | awk '$3=="dot_i8"{print $1}')
  printf "%-22s %-18s %d\n" "$b" "$a" $(( 0x$a % 64 ))
done
