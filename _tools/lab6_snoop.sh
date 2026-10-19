#!/bin/bash
# 查"membus 挂载时数据到底是谁给的"：看 snoop 相关的统计
cd /mnt/smartssd/wlx/cssys || exit 1
for p in "$@"; do
  echo "===== $p ====="
  awk '/Begin Simulation Statistics/{n++} n==2' out/sweeps/lab6_where_pe/$p/stats.txt \
  | grep -iE 'snoop|writeback|writeclean|cacheResponding|ReadRespWithInvalidate|ReadExResp' \
  | awk '$2+0 != 0 {printf "%-70s %s\n", $1, $2}'
done
