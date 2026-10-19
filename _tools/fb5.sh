#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
for v in qnn_dotp8x4 qnn_dotp8x4c; do
  python3 framework/sweep.py --name lab5_fb_$v --bench $v \
    --bench-args "8 0x01352505" --base "--cpu o3 --dotp8-lat 3" \
    --vary fetch-buffer=16,32,64 --jobs 3 >/dev/null 2>&1
  echo "--- $v ---"
  python3 framework/report.py results/lab5_fb_$v.csv \
    cycles insts fetch_cache_lines icache_stall_cycles lq_full_events
done
echo FBDONE
