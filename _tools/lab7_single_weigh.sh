#!/bin/bash
cd /mnt/smartssd/wlx/cssys || exit 1
for k in s_l1i s_l1d s_l2 s_width s_rob s_iq s_regs; do
  echo "### $k"
  python3 framework/area.py out/sweeps/lab7_$k/p* --csv
  echo
done
echo SINGLEWEIGHDONE
