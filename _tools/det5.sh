#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
G=gem5/build/RISCV/gem5.opt
B=bench/bin/riscv/qnn_dotp8x4c
run() {
  $G --outdir=/tmp/det$1 framework/cssys_se.py --cmd $B \
     --options "8 0x01352505" --cpu o3 --dotp8-lat 3 $2 >/dev/null 2>&1
  awk '/Begin Simulation Statistics/{n++} n==2 && \
       (/^system.cpu.numCycles /||/^system.dcache.overallMshrMisses::total /||\
        /^system.cpu.fetchStats0.cacheLines /)' /tmp/det$1/stats.txt \
    | awk -v t="$1" '{printf "%-10s %-55s %s\n", t, $1, $2}'
}
run A ""
run B ""
run C "--fetch-buffer 64"
echo DETDONE
