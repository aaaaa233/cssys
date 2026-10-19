#!/bin/bash
# 把任务 1 四格表里每一格的 accel.jobs / accel.macs 拉出来。
cd /mnt/smartssd/wlx/cssys || exit 1
for d in nf_timing_qnn_accel nf_timing_qnn_accel_nofence \
         nf_o3_qnn_accel nf_o3_qnn_accel_nofence \
         nopatch_timing nopatch_o3; do
  f=out/lab6/$d/stats.txt
  [ -f "$f" ] || { echo "$d  (no stats)"; continue; }
  j=$(grep -E '^system\.accel\.jobs ' "$f" | awk '{print $2}')
  m=$(grep -E '^system\.accel\.macs ' "$f" | awk '{print $2}')
  c=$(grep -E '^system\.accel\.jobCycles ' "$f" | awk '{print $2}')
  printf '%-32s jobs=%-6s macs=%-10s jobCycles=%s\n' "$d" "$j" "$m" "$c"
done
echo JOBSDONE
