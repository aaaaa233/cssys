#!/bin/bash
# Does the spelling of argv[0] change the measured cycle count?
# In gem5 SE mode argv[0] is copied onto the simulated process's initial
# stack, so a longer path shifts every stack address downward.
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt

run() {
  tag=$1; path=$2
  $G --outdir=/tmp/arg$tag framework/cssys_se.py --cmd "$path" \
     --options "8 0x01352505" --cpu o3 --dotp8-lat 3 >/dev/null 2>&1
  awk '/Begin Simulation Statistics/{n++} n==2 &&
       (/^system.cpu.numCycles /||
        /^system.cpu.fetch.cacheLines /||
        /^system.cpu.dcache.overallMshrMisses::total /||
        /^system.cpu.lsq0.thread0.numLoads /)' /tmp/arg$tag/stats.txt \
    | awk -v t="$tag" -v n="${#path}" \
        '{printf "%-4s len=%-3s %-48s %s\n", t, n, $1, $2}'
}

run R "bench/bin/riscv/qnn_dotp8x4c"
run S "/mnt/smartssd/wlx/cssys/bench/bin/riscv/qnn_dotp8x4c"
run T "/mnt/smartssd/wlx/cssys/./bench/bin/riscv/qnn_dotp8x4c"
run U "/mnt/smartssd/wlx/cssys/.//bench/bin/riscv/qnn_dotp8x4c"
echo ARGDONE
