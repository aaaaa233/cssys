#!/bin/bash
# Is the x2 "12815" anomaly a stack-layout artifact too?
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt

run() {
  tag=$1; path=$2
  $G --outdir=/tmp/x2$tag framework/cssys_se.py --cmd "$path" \
     --options "8 0x01352505" --cpu o3 --dotp8-lat 3 >/dev/null 2>&1
  awk '/Begin Simulation Statistics/{n++} n==2 &&
       (/^system.cpu.numCycles /||
        /^system.cpu.dcache.overallMshrMisses::total /||
        /^system.cpu.dcache.overallMisses::total /)' /tmp/x2$tag/stats.txt \
    | awk -v t="$tag" -v n="${#path}" \
        '{printf "%-4s len=%-3s %-48s %s\n", t, n, $1, $2}'
}

run A "/mnt/smartssd/wlx/cssys/bench/bin/riscv/qnn_dotp8x2"
run B "/mnt/smartssd/wlx/cssys/./bench/bin/riscv/qnn_dotp8x2"
run C "/mnt/smartssd/wlx/cssys/.//bench/bin/riscv/qnn_dotp8x2"
run D "/mnt/smartssd/wlx/cssys/.///bench/bin/riscv/qnn_dotp8x2"
echo X2DONE
