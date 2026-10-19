#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
for d in out/sweeps/lab5_*/p*/; do
  c=$(grep -m1 '^cmd=' "$d/config.ini")
  printf '%-56s %s\n' "$d" "$c"
done
echo SEEDDONE
