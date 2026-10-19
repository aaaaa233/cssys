#!/bin/bash
# 等三个参考数据脚本都跑完
cd /mnt/smartssd/wlx/cssys || exit 1
for i in $(seq 1 240); do
  a=0; b=0; c=0
  grep -q CHECKDONE  out/lab7_check.log  2>/dev/null && a=1
  grep -q CHECK2DONE out/lab7_check2.log 2>/dev/null && b=1
  grep -q FINALDONE  out/lab7_final.log  2>/dev/null && c=1
  if [ $a = 1 ] && [ $b = 1 ] && [ $c = 1 ]; then echo ALLDONE; exit 0; fi
  sleep 15
done
echo "TIMEOUT check=$a check2=$b final=$c"
