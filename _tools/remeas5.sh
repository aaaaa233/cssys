#!/bin/bash
# Re-measure every Lab 5 data point against the CURRENT binaries.
# The original tables were taken at 03:41; bench/src/qnn.c and all
# qnn_dotp8* binaries were rebuilt at 03:49, which shifted code layout.
cd /mnt/smartssd/wlx/cssys || exit 1

BA="8 0x01352505"
BASE="--cpu o3 --dotp8-lat 3"

# --- main table: one point per binary, all six in parallel -------------
for v in qnn qnn_dotp8 qnn_dotp8u4 qnn_dotp8x2 qnn_dotp8x4 qnn_dotp8x4c; do
  python3 framework/sweep.py --name lab5b_$v --bench $v \
      --bench-args "$BA" --base "$BASE" --jobs 1 >/dev/null 2>&1 &
done
wait
echo MAINDONE

# --- latency sweep: three binaries x six latencies ---------------------
for v in qnn_dotp8 qnn_dotp8x2 qnn_dotp8x4c; do
  python3 framework/sweep.py --name lab5b_lat_$v --bench $v \
      --bench-args "$BA" --base "--cpu o3" \
      --vary dotp8-lat=1,2,3,4,6,8 --jobs 6 >/dev/null 2>&1 &
done
wait
echo LATDONE
