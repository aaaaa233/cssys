#!/bin/bash
# Clean single-variable test: same binary, same config, ONLY the seed changes.
# This is what actually differs between two students.
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt

for v in qnn qnn_dotp8 qnn_dotp8x4 qnn_dotp8x4c; do
  for s in "8" "8 0x01352505" "8 0x00001234" "8 0xdeadbeef"; do
    tag=$(echo "$s" | tr -d ' ')
    $G --outdir=/tmp/sd_${v}_${tag} framework/cssys_se.py \
       --cmd bench/bin/riscv/$v --options "$s" \
       --cpu o3 --dotp8-lat 3 >/dev/null 2>&1
    line=$(awk '/Begin Simulation Statistics/{n++}
                n==2 && (/^system.cpu.numCycles /||/^system.cpu.committedInsts /)' \
           /tmp/sd_${v}_${tag}/stats.txt | awk '{printf "%s ", $2}')
    printf '%-14s seed="%-14s" cycles/insts = %s\n' "$v" "$s" "$line"
  done
done
echo SEEDVARDONE
