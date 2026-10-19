#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
A=out/lab1/roi/stats.txt
B=out/sweeps/lab1_cpu_models/p003_cpu-o3/stats.txt
for f in "$A" "$B"; do
  echo "== $f"
  awk '/Begin Simulation Statistics/{n++} n==2' "$f" \
    | grep -E '^(simInsts|simTicks|system.cpu.numCycles|system.cpu.ipc) '
done
echo "-- 命令行"
grep -m1 'command line' out/lab1/roi/config.ini 2>/dev/null
grep -m1 'command line' out/sweeps/lab1_cpu_models/p003_cpu-o3/config.ini 2>/dev/null
echo "-- config.ini 差异（前 40 行）"
diff out/lab1/roi/config.ini out/sweeps/lab1_cpu_models/p003_cpu-o3/config.ini | head -40
echo DIFFROIDONE
